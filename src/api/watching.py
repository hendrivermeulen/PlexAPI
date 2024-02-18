import threading
import time

from src.api.plex import PlexAPI
from src.api.qtorrent import QTorrentAPI

stop_semaphore = threading.Semaphore(0)


class WatchingListener(threading.Thread):

    def __init__(self):
        super().__init__()
        self.plex_api = PlexAPI()
        self.qtorrent = QTorrentAPI(self.plex_api)
        self.alert_listener = self.plex_api.server.startAlertListener(self.listen)
        self.playing = None
        threading.Thread(target=self.start_stop_timeout()).start()

    def listen(self, data):
        if data['type'] == "playing":
            notification = data["PlaySessionStateNotification"][0]
            if notification["state"] in ["buffering", "playing"]:
                for session in self.plex_api.server.sessions():
                    for item in session:
                        title = self.plex_api.get_name(item)
                        # stop previous
                        if self.playing is not None:
                            self.qtorrent.pause_torrent(self.playing)
                        self.playing = self.qtorrent.stream_torrent(True, title)
                        break
                    break
            elif notification["state"] == "stopped":
                print("Stopped playing")
                stop_semaphore.release()
                pass

    def start_stop_timeout(self):
        while True:
            stop_semaphore.acquire()
            temp = self.playing
            time.sleep(15)
            if temp == self.playing:
                if self.playing is not None:
                    self.qtorrent.pause_torrent(self.playing)
                else:
                    print("Nothing to pause")

    def run(self):
        self.alert_listener.join()


if __name__ == "__main__":
    WatchingListener().start()
