import string
import threading
import uuid
from enum import Enum

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from utils.stoppable_thread import StoppableThread


class TYPE(Enum):
    MOVIE = "MOVIE"
    SERIES = "SERIES"


class Request:
    def __init__(self, title: string, request_type: TYPE):
        self.title = title
        self.request_type = request_type
        self.request_id = uuid.uuid4()
        self.response = None


class TorrentBrowser(StoppableThread):
    def __init__(self):
        super().__init__("TorrentBrowser", should_loop=True, loop_sleep_time_s=0)
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.requests: list[Request] = []
        self.requests_lock = threading.Semaphore(0)
        self.responses: list[Request] = []
        self.responses_queue = threading.Semaphore(0)
        self.responses_lock = threading.Lock()

    def work(self):
        self.requests_lock.acquire()
        if self.is_running:
            request = self.requests.pop()
            if request.request_type is TYPE.MOVIE:
                request.response = self.movie_search(request.title)
            else:
                request.response = self.series_search(request.title)
            self.clean_up()
            with self.responses_lock:
                self.responses.append(request)
                self.responses_queue.release()

    def on_stop(self):
        self.requests_lock.release()
        self.responses_queue.release()
        self.clean_up()

    def add_concurrent_request(self, title: string, request_type: TYPE):
        request = Request(title, request_type)
        self.requests.append(request)
        self.requests_lock.release()
        return request

    def await_request(self, request: Request):
        result = None
        while result is None:
            self.responses_queue.acquire()
            if self.is_running:
                with self.responses_lock:
                    if request in self.responses:
                        result = self.responses.pop(self.responses.index(request)).response
        return result

    def movie_search(self, title: string):
        raise NotImplementedError()

    def series_search(self, title: string):
        raise NotImplementedError()

    def clean_up(self):
        try:
            self.driver.close()
        except:
            pass
