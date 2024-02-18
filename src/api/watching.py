import threading
import time
from pprint import pprint

from plexapi.media import TranscodeSession
from plexapi.playqueue import PlayQueue

from src.api.plex import PlexAPI
from src.api.qtorrent import QTorrentAPI


class WatchingListener(threading.Thread):

    def __init__(self):
        super().__init__()
        self.plex_api = PlexAPI()
        self.qtorrent = QTorrentAPI(self.plex_api)
        self.alert_listener = self.plex_api.server.startAlertListener(self.test)

    def test(self, data):
        if data['type'] == "playing":
            notification = data["PlaySessionStateNotification"][0]
            if notification["state"] == "playing":
                for session in self.plex_api.server.sessions():
                    pprint(vars(session))
                    print(session.guid)
            elif notification["stopped"] == "playing":
                pass

    def run(self):
        self.alert_listener.join()


if __name__ == "__main__":
    WatchingListener().start()
