from api.plex import PlexAPI
from utils.stoppable_thread import StoppableThread
from workers.main_worker import MainWorker


class WatchlistScrapper(StoppableThread):

    def __init__(self, last_watchlist: list, worker: MainWorker):
        super().__init__(should_loop=True, stop_timeout_s=30)
        self.plex_api = PlexAPI()
        self.watchlist = last_watchlist
        self.worker = worker

    def work(self):
        updated_watchlist = self.plex_api.get_watchlist()
        old_watchlist = self.watchlist.copy()

        for item in updated_watchlist:
            item = self.plex_api.get_name(item)
            if item in self.watchlist:
                old_watchlist.remove(item)
            else:
                self.watchlist.append(item)
                self.worker.watchlist_item_added(item)

        for item in old_watchlist:
            self.watchlist.remove(item)
            self.worker.watchlist_item_removed(item)

