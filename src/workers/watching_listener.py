import threading

from api.plex import PlexAPI
from utils.logger import log
from utils.stoppable_thread import StoppableThread, StoppedException

stop_semaphore = threading.Semaphore(0)


class WatchingListener:
    def started_playing(self, item):
        raise NotImplementedError()

    def stopped_playing(self, item):
        raise NotImplementedError()


class WatchingNotifier(StoppableThread):

    def __init__(self, watching_listener: WatchingListener):
        super().__init__("WatchingNotifier")
        self.plex_api = PlexAPI()
        self.alert_listener = None
        self.watching_listener = watching_listener
        self.currently_playing = None

    def process_playing(self):
        for session in self.plex_api.server.sessions():
            for item in session:
                title = self.plex_api.get_name(item)
                if self.currently_playing is None or self.currently_playing is not title:
                    log("Started playing " + title)
                    self.currently_playing = title
                    self.watching_listener.started_playing(title)
                break
            break

    def process_stopped(self):
        log("Stopped playing " + self.currently_playing)
        self.watching_listener.stopped_playing(self.currently_playing)
        self.currently_playing = None

    def listen(self, data):
        if data['type'] == "playing":
            notification = data["PlaySessionStateNotification"][0]
            if notification["state"] in ["buffering", "playing"]:
                self.process_playing()
            elif notification["state"] == "stopped":
                self.process_stopped()

    def run(self):
        while self.is_running:
            self.alert_listener = self.plex_api.confirm_connection(
                lambda: self.plex_api.server.startAlertListener(self.listen))
            if self.alert_listener is None:
                try:
                    self.sleep(5)
                except StoppedException:
                    break
                continue
            self.alert_listener.join()

    def on_stop(self):
        if self.alert_listener is not None:
            self.alert_listener.stop()
