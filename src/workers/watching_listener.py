import threading
import time

from api.plex import PlexAPI
from api.qtorrent import QTorrentAPI
from utils.stoppable_thread import StoppableThread

stop_semaphore = threading.Semaphore(0)


class WatchingListener(StoppableThread):

    def __init__(self):
        super().__init__(name="WatchingListener")
        self.plex_api = PlexAPI()
        self.qtorrent = QTorrentAPI(self.plex_api)
        self.alert_listener = self.plex_api.server.startAlertListener(self.listen)
        self.playing = None
        self.playing_title = None
        self.currently_active = False
        self.stop_request_count = 0
        self.stop_lock = threading.Lock()
        self.play_lock = threading.Lock()
        threading.Thread(target=self.start_stop_timeout()).start()

    def listen(self, data):
        self.play_lock.acquire()
        self.check_for_playing(data)
        self.play_lock.release()

    def check_for_playing(self, data):
        if data['type'] == "playing":
            notification = data["PlaySessionStateNotification"][0]
            if notification["state"] in ["buffering", "playing"]:
                for session in self.plex_api.server.sessions():
                    for item in session:
                        title = self.plex_api.get_name(item)
                        previous = self.playing
                        self.currently_active = True
                        if self.playing_title == title:
                            return
                        else:
                            self.playing_title = title
                            current = self.qtorrent.stream_torrent(True, item)
                        # stop previous
                        if previous is not None and previous != current:
                            self.qtorrent.pause_torrent(previous, title)
                        self.playing = current
                        break
                    break
            elif notification["state"] == "stopped":
                self.currently_active = False
                stop_semaphore.release()

    def start_stop_timeout(self):
        while True:
            stop_semaphore.acquire()

            self.stop_lock.acquire()
            self.stop_request_count += 1
            temp = self.playing
            self.stop_lock.release()

            time.sleep(60)

            self.stop_lock.acquire()
            if self.stop_request_count == 1:
                self.play_lock.acquire()
                if temp == self.playing and not self.currently_active:
                    if self.playing is not None:
                        self.qtorrent.pause_torrent(self.playing, self.playing_title)
                        self.playing = None
                        self.playing_title = None
                    else:
                        print("Nothing to pause")
                self.play_lock.release()
            self.stop_request_count -= 1
            self.stop_lock.release()

    def run(self):
        self.alert_listener.join()


if __name__ == "__main__":
    WatchingListener().start()
