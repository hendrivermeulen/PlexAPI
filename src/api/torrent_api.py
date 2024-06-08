import string

from api.torrent.pirate_bay import PirateBayTorrentBrowser
from api.torrent.yts import YTSTorrentBrowser


class TorrentAPI:

    def __init__(self):
        self.pirate_bay = PirateBayTorrentBrowser()
        self.yts = YTSTorrentBrowser()

    def process(self, results: list):
        self.pirate_bay.stop()
        self.yts.stop()
        results = list(dict.fromkeys(results))
        return results

    def movie_search(self, title: string):
        return self.process(self.pirate_bay.movie_search(title) + self.yts.movie_search(title))

    def series_search(self, title: string):
        return self.process(self.pirate_bay.series_search(title))