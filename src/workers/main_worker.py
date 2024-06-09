import threading

from api.api import repeat_until_process
from api.plex import PlexAPI
from api.qtorrent import QTorrentAPI
from api.torrent.torrent_browser import sort_result
from api.torrent_api import TorrentAPI
from utils.logger import log
from utils.startable import Startable
from utils.stoppable_thread import StoppableThread
from workers.streamable_finder import StreamableFinder
from workers.watching_listener import WatchingListener, WatchingNotifier
from workers.watchlist_scrapper import WatchlistScrapper, WatchlistListener, VideoItem


class MainWorker(StoppableThread, WatchlistListener, WatchingListener):

    def __init__(self):
        super().__init__("MainWorker", should_loop=True, loop_sleep_time_s=60*5)
        self._startables = None
        self._watchlist_notifier = None
        self._watchlist_scrapper = None
        self._streamable_finder: StreamableFinder | None = None

        self._plex_api = PlexAPI()
        self._qtorrent_api = QTorrentAPI()
        self._torrent_api = TorrentAPI()

        self._currently_playing: str | None = None
        self._playing_lock: threading.RLock = threading.RLock()
        self._previously_playing = None
        self._previous_added_to_watchlist = None
        self._watchlist_lock = threading.Lock()

    def work(self):
        # TODO do not pause streamable findings
        for title in self._get_current_torrents():
            with self._playing_lock:
                if title == self._previously_playing:
                    self._previously_playing = None
                else:
                    with self._watchlist_lock:
                        if title == self._previous_added_to_watchlist:
                            self._previous_added_to_watchlist = None
                        else:
                            if title != self._currently_playing:
                                self._pause_torrent(title)

    def _get_current_torrents(self):
        torrents = repeat_until_process(
            lambda: self._qtorrent_api.get_current_titles(), self.sleep)
        if torrents is None:
            return []
        else:
            return torrents

    def started(self):
        last_watchlist = self._get_current_torrents()

        self._watchlist_scrapper = WatchlistScrapper(last_watchlist, self, self._plex_api)
        self._watchlist_notifier = WatchingNotifier(self, self._plex_api)
        self._streamable_finder = StreamableFinder(self._qtorrent_api)

        self._startables: list[Startable] = \
            [self._torrent_api, self._watchlist_scrapper, self._watchlist_notifier, self._streamable_finder]

        for startable in self._startables:
            startable.start()

    def before_stop(self):
        for startable in self._startables:
            startable.stop()

        for title in self._get_current_torrents():
            self._pause_torrent(title)

    def watchlist_item_added(self, video_item: VideoItem):
        with self._watchlist_lock:
            self._previous_added_to_watchlist = video_item.title
            magnets = self._torrent_api.movie_search(video_item.title)
            magnets.sort(key=sort_result)

            self._streamable_finder.add_request(video_item, magnets)

    def watchlist_item_removed(self, title):
        with self._watchlist_lock:
            if self._previous_added_to_watchlist == title:
                self._previous_added_to_watchlist = None
            if not self._streamable_finder.remove_request(title):
                repeat_until_process(lambda: self._qtorrent_api.delete_torrent(title), self.sleep)

    def started_playing(self, title):
        with self._playing_lock:
            if self._currently_playing != title:
                log("Started playing " + title)

                self._streamable_finder.pause()
                for torrent in self._get_current_torrents():
                    if torrent != title:
                        self._pause_torrent(torrent)

                self._currently_playing = title
                repeat_until_process(lambda: self._qtorrent_api.resume_torrent(title), self.sleep)

    def _pause_torrent(self, title):
        with self._playing_lock:
            if title is not None:
                repeat_until_process(lambda: self._qtorrent_api.pause_torrent(title), self.sleep)

    def stopped_playing(self, title):
        self._streamable_finder.resume()
        with self._playing_lock:
            log("Stopped playing " + title)
            if title != self._currently_playing:
                self._pause_torrent(title)
            else:
                self._previously_playing = title
                self._currently_playing = None
