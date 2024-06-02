from utils.stoppable_thread import StoppableThread


class MainWorker(StoppableThread):

    def __init__(self):
        super().__init__(should_loop=True)

    def work(self):
        pass

    def watchlist_item_added(self, item):
        pass

    def watchlist_item_removed(self, item):
        pass