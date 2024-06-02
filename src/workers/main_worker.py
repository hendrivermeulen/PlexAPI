from utils.stoppable_thread import StoppableThread
from workers.watchlist_scrapper import WatchlistScrapper, WatchlistListener


class MainWorker(StoppableThread, WatchlistListener):

    def __init__(self):
        super().__init__("MainWorker", should_loop=True)
        self.watchlist_scrapper = WatchlistScrapper([], self)

    def work(self):
        if self.running:
            pass

    def on_start(self):
        self.watchlist_scrapper.start()

    def on_stop(self):
        self.watchlist_scrapper.stop()

    def watchlist_item_added(self, item):
        pass

    def watchlist_item_removed(self, item):
        pass
