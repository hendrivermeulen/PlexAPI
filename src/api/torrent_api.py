import string

from api.torrent.pirate_bay import PirateBayTorrentBrowser
from api.torrent.torrent_browser import TYPE
from api.torrent.yts import YTSTorrentBrowser
from utils.startable import Startable


def process(results: list):
    return list(dict.fromkeys(results))


class TorrentAPI(Startable):

    def __init__(self):
        super().__init__()
        self.pirate_bay = PirateBayTorrentBrowser()
        self.yts = YTSTorrentBrowser()

    def on_start(self):
        self.pirate_bay.start()
        self.yts.start()

    def on_stop(self):
        self.pirate_bay.stop()
        self.yts.stop()

    def movie_search(self, title: string):
        pirate_bay_request = self.pirate_bay.add_concurrent_request(title, TYPE.MOVIE)
        yts_request = self.yts.add_concurrent_request(title, TYPE.MOVIE)
        return process(self.pirate_bay.await_request(pirate_bay_request)
                       + self.yts.await_request(yts_request))

    def series_search(self, title: string):
        yts_request = self.yts.add_concurrent_request(title, TYPE.SERIES)
        return process(self.yts.await_request(yts_request))
