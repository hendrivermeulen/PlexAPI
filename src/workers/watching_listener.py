import threading

from api.plex import PlexAPI
from utils.logger import log
from utils.stoppable_thread import StoppableThread

stop_semaphore = threading.Semaphore(0)


class WatchingListener:
    def started_playing(self, title):
        raise NotImplementedError()

    def stopped_playing(self, title):
        raise NotImplementedError()


class WatchingNotifier(StoppableThread):

    def __init__(self, watching_listener: WatchingListener, plex_api: PlexAPI):
        super().__init__("WatchingNotifier", should_loop=True)
        self.plex_api = plex_api
        self.alert_listener = None
        self.watching_listener = watching_listener
        self.currently_playing = None

    def process_playing(self):
        sessions = self.plex_api.get_sessions()
        if sessions is not None:
            for session in sessions:
                for item in session:
                    title = self.plex_api.get_name(item)
                    if self.currently_playing is None or self.currently_playing is not title:
                        self.currently_playing = title
                        self.watching_listener.started_playing(title)
                    break
                break

    def process_stopped(self):
        self.watching_listener.stopped_playing(self.currently_playing)
        self.currently_playing = None

    def listen(self, data):
        if data['type'] == "playing":
            notification = data["PlaySessionStateNotification"][0]
            if notification["state"] in ["buffering", "playing"]:
                self.process_playing()
            elif notification["state"] == "stopped":
                self.process_stopped()

    def work(self):
        self.alert_listener = self.plex_api.confirm_connection(
            lambda: self.plex_api.start_alert_listener(self.listen))
        if self.alert_listener is None:
            self.sleep(5)
        else:
            self.alert_listener.join()

    def before_stop(self):
        if self.alert_listener is not None:
            self.alert_listener.stop()
