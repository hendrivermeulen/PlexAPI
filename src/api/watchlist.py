import os
import threading
import time
import traceback

from src.api.plex import PlexAPI
from src.api.torrent import TorrentBrowser
from src.api.utils import contains_at_least_half
from src.api.qtorrent import QTorrentAPI


class WatchlistScrapper(threading.Thread):

    def __init__(self):
        super().__init__()
        self.plex_api = PlexAPI()
        self.torrent_api = TorrentBrowser()
        self.qtorrent = QTorrentAPI(self.plex_api)
        self.no_torrents = []
        self.time_passed_seconds = 0
        self.alreadyHave = []

        for item in self.plex_api.get_watchlist():
            title = self.plex_api.get_name(item)
            alreadyHas = False
            for torrent in self.qtorrent.get_torrents():
                if contains_at_least_half(title, torrent.name):
                    alreadyHas = True
                    break

            if alreadyHas:
                self.alreadyHave.append(title)

    def run(self):
        self.qtorrent.start()
        while True:
            try:
                sleep_time_seconds = 1
                self.update()
                time.sleep(sleep_time_seconds)
                self.time_passed_seconds += sleep_time_seconds
            except Exception as e:
                traceback.print_exc()

    def update(self):
        for item in self.plex_api.get_watchlist():
            title = self.plex_api.get_name(item)

            if title in self.alreadyHave:
                continue

            if self.time_passed_seconds > 60 * 60 * 24:  # one day
                self.no_torrents = []
                self.time_passed_seconds = 0

            if item.type == "movie":
                if title in os.listdir(self.plex_api.library_path + "/Movies"):
                    continue
            else:
                if title in os.listdir(self.plex_api.library_path + "/TV-Shows"):
                    continue

            if item not in self.no_torrents:
                urls = None
                if item.type == "movie":
                    print("Looking for Movie:", title)
                    urls = self.torrent_api.movie_search(title)
                else:
                    print("TV Show not yet supported")
                    continue

                if urls is not None and len(urls) > 0:
                    for url in urls:
                        print("Adding", url)
                        if self.qtorrent.add_torrent(url, item.type == "movie", title):
                            print("Found streamable: ", url)
                            break
                        else:
                            print("Not streamable")
                    self.alreadyHave.append(title)
                else:
                    self.no_torrents.append(item)
