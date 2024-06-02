import threading
from threading import Thread

from utils.logger import log

class StoppableThread(Thread):

    def __init__(self, should_loop=False, loop_sleep_time_s=1, enable_tick_tock=False, stop_timeout_s = 10):
        super().__init__()
        self.enable_tick_tock = enable_tick_tock
        self.sleep_lock = threading.Semaphore(0)
        self.stopped_lock = threading.Semaphore(0)
        self.tick_tock_lock = threading.Semaphore(0)

        self.stop_timeout_s = stop_timeout_s

        self.running = False
        self.should_loop = should_loop
        self.loop_sleep_time_s = loop_sleep_time_s

    def sleep(self, time_s):
        if self.do_sleep(time_s):
            raise StoppedException()

    def do_sleep(self, time_s):
        if self.enable_tick_tock:
            return not self.tick_tock_lock.acquire(True) and self.running
        else:
            return self.sleep_lock.acquire(True, time_s)

    def run(self):
        self.running = True
        if self.should_loop:
            try:
                while self.running:
                    try:
                        self.work()
                    except Exception as e:
                        if isinstance(e, StoppedException):
                            raise e
                        else:
                            log(exception=e)
                    self.sleep(self.loop_sleep_time_s)
            except StoppedException:
                pass
        else:
            self.work()
        self.stopped_lock.release()
        self.running = False

    def work(self):
        pass

    def stop(self):
        self.running = False
        self.sleep_lock.release()
        self.tock()
        if not self.stopped_lock.acquire(True, self.stop_timeout_s):
            raise StopTimeoutException()

    def tock(self):
        self.tick_tock_lock.release()


class StopTimeoutException(Exception):
    pass


class StoppedException(Exception):
    pass
