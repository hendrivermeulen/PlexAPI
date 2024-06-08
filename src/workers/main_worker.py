import threading

from api.plex import PlexAPI
from api.qtorrent import QTorrentAPI
from api.torrent_api import TorrentAPI
from utils.logger import log
from utils.startable import Startable
from utils.stoppable_thread import StoppableThread
from workers.streamable_finder import find_streamable
from workers.watching_listener import WatchingListener, WatchingNotifier
from workers.watchlist_scrapper import WatchlistScrapper, WatchlistListener, VideoItem


class MainWorker(StoppableThread, WatchlistListener, WatchingListener):

    def __init__(self):
        super().__init__("MainWorker", should_loop=True)
        self._plex_api = PlexAPI()
        self._qtorrent_api = QTorrentAPI()
        self._torrent_api = TorrentAPI()

        # TODO load in title from qtorrent
        self._watchlist_scrapper = WatchlistScrapper([], self, self._plex_api)
        self._watchlist_notifier = WatchingNotifier(self, self._plex_api)

        self._startables: list[Startable] = [self._torrent_api, self._watchlist_scrapper, self._watchlist_notifier]

        self._currently_playing: str | None = None
        self._playing_lock: threading.RLock = threading.RLock()

    def work(self):
        # TODO clean up, pause torrents not being played
        pass

    def before_starting(self):
        for startable in self._startables:
            startable.start()

    def before_stop(self):
        for startable in self._startables:
            startable.stop()

        # TODO pause all

    def watchlist_item_added(self, video_item: VideoItem):
        # TODO add to streamable queue, pause other already found streamable
        magnets = self._torrent_api.movie_search(video_item.title)
        if find_streamable(video_item, magnets, self._qtorrent_api, self.sleep):
            log("Found streamable for " + video_item.title)
        else:
            log(video_item.title + " not streamable")

    def watchlist_item_removed(self, title):
        # TODO remove from streamable finder
        self._qtorrent_api.repeat_until_process(lambda: self._qtorrent_api.delete_torrent(title), self.sleep)

    def started_playing(self, title):
        # TODO pause all except playing
        with self._playing_lock:
            self.stopped_playing(self._currently_playing)
            self._currently_playing = title
            self._qtorrent_api.repeat_until_process(lambda: self._qtorrent_api.resume_torrent(title), self.sleep)

    def stopped_playing(self, title):
        # TODO resume streamable finder
        with self._playing_lock:
            if title is not None:
                self._qtorrent_api.repeat_until_process(lambda: self._qtorrent_api.pause_torrent(title), self.sleep)
