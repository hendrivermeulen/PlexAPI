import threading

from api.api import repeat_until_process
from api.qtorrent import QTorrentAPI
from api.torrent.torrent_browser import Result
from utils.logger import log
from utils.stoppable_thread import StoppableThread
from workers.watchlist_scrapper import VideoItem


class Request:
    def __init__(self, video_item: VideoItem, results: list[Result]):
        self.video_item = video_item
        self.results = results


class StreamableFinder(StoppableThread):

    def __init__(self, qtorrent: QTorrentAPI):
        super().__init__("StreamableFinder", should_loop=True, loop_sleep_time_s=-1)
        self._qtorrent = qtorrent
        self._request_lock = threading.RLock()
        self._wait_time_s = 10
        self._latest_request: Request | None = None
        self._backlog = []
        self._is_paused = False

    def request_cancelled(self, request: Request, cancelled: True):
        if not cancelled:
            self._backlog.append(request)
        repeat_until_process(lambda: self._qtorrent.delete_torrent(request.video_item.title), self.sleep)
        self.tock()

    def work(self):
        with self._request_lock:
            if self._is_paused:
                return

            if self._latest_request is None:
                if len(self._backlog) > 0:
                    request = self._backlog.pop()
                    self._latest_request = request
                else:
                    return
            else:
                request = self._latest_request

        try:
            if request is not None:
                self._find_streamable(request)
        except RequestChangedException:
            self.request_cancelled(request, False)
        except RequestCancelledException:
            self.request_cancelled(request, not self._is_paused)

    def add_request(self, video_item: VideoItem, results: list[Result]):
        with self._request_lock:
            self._latest_request = Request(video_item, results)
            self.tock()

    def remove_request(self, title: str):
        with self._request_lock:
            if self._latest_request is not None and self._latest_request.video_item.title == title:
                self._latest_request = None
                return True
            else:
                for request in self._backlog:
                    if request.video_item.title == title:
                        self._backlog.remove(request)
                        return True
        return False

    def pause(self):
        with self._request_lock:
            log("Pausing streamable finder")
            self._is_paused = True
            self._latest_request = None

    def resume(self):
        with self._request_lock:
            log("Resuming streamable finder")
            self._is_paused = False
            self.tock()

    def _add_torrent(self, magnet: str, video_item: VideoItem):
        repeat_until_process(
            lambda: self._qtorrent.add_torrent(magnet, video_item.is_movie, video_item.title), self.sleep)
        torrents = repeat_until_process(
            lambda: self._qtorrent.get_current_titles(), self.sleep)
        if video_item.title not in torrents:
            raise RuntimeError("Torrent add failed")

    def _confirm_streamable(self, request: Request):
        count = 0
        prev_eta = 100 * 365 * 24 * 3600  # 100 years

        video_item = request.video_item

        is_streamable = False
        while count < 3:
            eta = repeat_until_process(lambda: self._qtorrent.get_torrent_eta(video_item.title),
                                       self.sleep)
            if eta == -1:
                raise RuntimeError("Torrent ETA not found")

            if eta < video_item.duration_s * 0.70:
                is_streamable = True
                break

            self.sleep(self._wait_time_s)
            with self._request_lock:
                if self._latest_request is None:
                    raise RequestCancelledException()
                if self._latest_request != request:
                    raise RequestChangedException()

            if eta - prev_eta < self._wait_time_s * 2:
                log("Speeding up")
                count = 0
            else:
                log("Too slow")
                count += 1
            prev_eta = eta

        return is_streamable

    def _find_streamable(self, request: Request):
        log("Looking for streamable for " + request.video_item.title)
        video_item = request.video_item
        for result in request.results:
            self._add_torrent(result.magnet, video_item)
            log("Attempting")
            if self._confirm_streamable(request):
                log("Found streamable " + video_item.title)
                return True
            else:
                log("Failed")
                repeat_until_process(lambda: self._qtorrent.delete_torrent(video_item.title), self.sleep)
        log(video_item.title + " not streamable")
        return False


class RequestChangedException(Exception):
    pass


class RequestCancelledException(Exception):
    pass
