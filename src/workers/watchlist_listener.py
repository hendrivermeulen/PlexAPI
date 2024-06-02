import os
import threading
import time
import traceback

from api.plex import PlexAPI
from api.torrent import TorrentBrowser
from utils.logger import log
from utils.stoppable_thread import StoppableThread, StoppedException
from utils.utils import contains_at_least_half
from api.qtorrent import QTorrentAPI
from workers.main_worker import watchlist_item_added, watchlist_item_removed


class WatchlistScrapper(StoppableThread):

    def __init__(self):
        super().__init__(should_loop=True)
        self.plex_api = PlexAPI()
        self.watchlist = []

    def run(self):
        updated_watchlist = self.plex_api.get_watchlist()
        old_watchlist = self.watchlist.copy()

        for item in updated_watchlist:
            if item in self.watchlist:
                old_watchlist.remove(item)
            else:
                watchlist_item_added(item)

        for item in old_watchlist:
            watchlist_item_removed(item)

