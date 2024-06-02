from api.plex import PlexAPI
from utils.logger import log, log_error
from utils.stoppable_thread import StoppableThread


class WatchlistListener:
    def watchlist_item_added(self, item):
        pass

    def watchlist_item_removed(self, item):
        pass


class WatchlistScrapper(StoppableThread):

    def __init__(self, last_watchlist: list, listener: WatchlistListener):
        super().__init__(name="WatchlistScrapper", should_loop=True, stop_timeout_s=30)
        self.plex_api = None
        self.watchlist = last_watchlist
        self.plex_api = PlexAPI()
        self.listener = listener
        self.connected = False

    def work(self):
        try:
            self.plex_api.on_start()
            if not self.connected:
                self.connected = True
                log("Connected to Plex")
        except Exception:
            self.connected = False
            timeout = 4
            log_error("Lost connection to Plex, trying again in " + str(timeout+1) + " seconds...")
            self.sleep(timeout)
            return

        updated_watchlist = self.plex_api.get_watchlist()
        old_watchlist = self.watchlist.copy()

        for item in updated_watchlist:
            item = self.plex_api.get_name(item)
            if item in self.watchlist:
                old_watchlist.remove(item)
            else:
                self.watchlist.append(item)
                self.listener.watchlist_item_added(item)

        for item in old_watchlist:
            self.watchlist.remove(item)
            self.listener.watchlist_item_removed(item)

