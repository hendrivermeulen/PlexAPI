from utils.stoppable_thread import StoppableThread
from workers.watching_listener import WatchingListener, WatchingNotifier
from workers.watchlist_scrapper import WatchlistScrapper, WatchlistListener


class MainWorker(StoppableThread, WatchlistListener, WatchingListener):

    def __init__(self):
        super().__init__("MainWorker", should_loop=True)
        self.watchlist_scrapper = WatchlistScrapper([], self)
        self.watchlist_notifier = WatchingNotifier(self)

    def work(self):
        pass

    def before_starting(self):
        self.watchlist_scrapper.start()
        self.watchlist_notifier.start()

    def before_stop(self):
        self.watchlist_scrapper.stop()
        self.watchlist_notifier.stop()

    def watchlist_item_added(self, item):
        pass

    def watchlist_item_removed(self, item):
        pass

    def started_playing(self, item):
        pass

    def stopped_playing(self, item):
        pass
