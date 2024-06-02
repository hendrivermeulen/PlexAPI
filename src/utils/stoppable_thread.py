import threading
from threading import Thread
from utils.logger import log


class StoppableThread:

    def __init__(self, should_loop=False, loop_sleep_time_s=1, stop_timeout_s=10):
        super().__init__()
        self.thread = None
        self.sleep_lock = threading.Semaphore(0)
        self.stopped_lock = threading.Semaphore(0)

        self.stop_timeout_s = stop_timeout_s

        self.running = False
        self.should_loop = should_loop
        self.loop_sleep_time_s = loop_sleep_time_s

    def sleep(self, time_s):
        if not self.do_sleep(time_s):
            raise StoppedException()

    def do_sleep(self, time_s):
        return not self.sleep_lock.acquire(True, time_s) or self.running

    def is_running(self):
        return self.running

    def run(self):
        if self.should_loop:
            try:
                while self.is_running():
                    self.apply_work()
                    self.sleep(self.loop_sleep_time_s)
            except StoppedException:
                pass
        else:
            self.apply_work()
        self.stopped_lock.release()
        self.running = False

    def apply_work(self):
        try:
            self.work()
        except Exception as e:
            if isinstance(e, StoppedException):
                raise e
            else:
                log(exception=e)

    def work(self):
        raise NoWorkException()

    def start(self):
        if self.running:
            raise AlreadyRunningException()
        else:
            self.thread = Thread(target=self.run)
            self.running = True
            self.thread.start()

    def stop(self):
        if self.running:
            self.running = False
            self.tock()
            if not self.stopped_lock.acquire(True, self.stop_timeout_s):
                raise StopTimeoutException()
            self.thread.join()
        else:
            raise NotRunningException

    def tock(self):
        self.sleep_lock.release()


class StopTimeoutException(Exception):
    pass


class StoppedException(Exception):
    pass


class AlreadyRunningException(Exception):
    pass


class NotRunningException(Exception):
    pass


class NoWorkException(Exception):
    pass
