from utils.stoppable_thread import StoppableThread


def watchlist_item_added(item):
    pass

def watchlist_item_removed(item):
    pass

class MainWorker(StoppableThread):

    def __init__(self):
        super().__init__(should_loop=True)

    def work(self):
        pass