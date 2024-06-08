from api.plex import PlexAPI
from utils.logger import log
from utils.stoppable_thread import StoppableThread


class VideoItem:
    def __init__(self, title: str, duration_s: float, is_movie: bool):
        self.title = title
        self.duration_s = duration_s
        self.is_movie = is_movie


class WatchlistListener:
    def watchlist_item_added(self, video_item: VideoItem):
        raise NotImplementedError()

    def watchlist_item_removed(self, title):
        raise NotImplementedError()


class WatchlistScrapper(StoppableThread):

    def __init__(self, last_watchlist: list, listener: WatchlistListener, plex_api: PlexAPI):
        super().__init__(name="WatchlistScrapper", should_loop=True, stop_timeout_s=30)
        self.plex_api = plex_api
        self.watchlist = last_watchlist
        self.listener = listener

    def work(self):
        updated_watchlist = self.plex_api.get_watchlist()
        if updated_watchlist is None:
            self.sleep(5)
        else:
            old_watchlist = self.watchlist.copy()

            for item in updated_watchlist:
                title = self.plex_api.get_name(item)
                video_item = VideoItem(title, item.duration/1000, item.type == "movie")

                if video_item.title in self.watchlist:
                    old_watchlist.remove(title)
                else:
                    self.watchlist.append(title)
                    log("Added " + title + " to watchlist")
                    self.listener.watchlist_item_added(video_item)

            for title in old_watchlist:
                self.watchlist.remove(title)
                log("Removed " + title + " from watchlist")
                self.listener.watchlist_item_removed(title)
