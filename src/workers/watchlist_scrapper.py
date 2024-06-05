from api.plex import PlexAPI
from utils.logger import log
from utils.stoppable_thread import StoppableThread


class WatchlistListener:
    def watchlist_item_added(self, item):
        pass

    def watchlist_item_removed(self, item):
        pass


class WatchlistScrapper(StoppableThread):

    def __init__(self, last_watchlist: list, listener: WatchlistListener):
        super().__init__(name="WatchlistScrapper", should_loop=True, stop_timeout_s=30)
        self.plex_api: PlexAPI | None = None
        self.watchlist = last_watchlist
        self.listener = listener
        self.plex_api = PlexAPI()

    def work(self):
        updated_watchlist = self.plex_api.get_watchlist()
        if updated_watchlist is None:
            self.sleep(5)
        else:
            old_watchlist = self.watchlist.copy()

            for item in updated_watchlist:
                item = self.plex_api.get_name(item)
                if item in self.watchlist:
                    old_watchlist.remove(item)
                else:
                    self.watchlist.append(item)
                    log("Added " + item + " to watchlist")
                    self.listener.watchlist_item_added(item)

            for item in old_watchlist:
                self.watchlist.remove(item)
                log("Removed " + item + " from watchlist")
                self.listener.watchlist_item_removed(item)
