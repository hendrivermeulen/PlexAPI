import threading
from unittest import TestCase

from utils.logger import logged_exceptions
from utils.stoppable_thread import StoppableThread, StoppedException, StopTimeoutException, NotRunningException, \
    AlreadyRunningException, NoWorkException

TIMEOUT = 10

work_done = threading.Semaphore(0)
stopped = threading.Semaphore(0)
stop = threading.Semaphore(0)


class TestThread(StoppableThread):

    def work(self):
        while self.is_running():
            work_done.release(1)
            try:
                self.sleep(10)
            except StoppedException:
                stopped.release()


class TestLoopSleepThread(StoppableThread):

    def __init__(self):
        super().__init__(should_loop=True)

    def work(self):
        self.sleep(10)


class TestUnstoppableThread(StoppableThread):

    def __init__(self):
        super().__init__(stop_timeout_s=1)

    def work(self):
        stop.acquire()
        stopped.release()


class TestExceptionLoopThread(StoppableThread):

    def __init__(self):
        super().__init__(should_loop=True)

    def work(self):
        work_done.release(1)
        raise Exception("Test")


class LoopTestThread(StoppableThread):

    def __init__(self):
        super().__init__(should_loop=True)

    def work(self):
        work_done.release(1)


class Test(TestCase):
    def setUp(self):
        self.test_thread = None

    def tearDown(self):
        if self.test_thread is not None and self.test_thread.running:
            self.test_thread.stop()

    def test_stoppable_thread(self):
        self.test_thread = TestThread()
        self.test_thread.start()
        self.assertTrue(work_done.acquire(True, TIMEOUT))
        self.test_thread.stop()
        self.assertTrue(stopped.acquire(True, TIMEOUT))

    def test_unstoppable_thread(self):
        self.test_thread = TestUnstoppableThread()
        self.test_thread.start()
        self.assertRaises(StopTimeoutException, self.test_thread.stop)
        stop.release()

    def test_loop_stoppable_thread(self):
        self.test_thread = LoopTestThread()
        self.test_thread.start()
        self.assertTrue(work_done.acquire(True, TIMEOUT))
        self.test_thread.stop()

    def test_loop_tick_tock_stoppable_thread(self):
        self.test_thread = LoopTestThread()
        self.test_thread.start()
        self.assertTrue(work_done.acquire(True, TIMEOUT))
        self.test_thread.tock()
        self.assertTrue(work_done.acquire(True, TIMEOUT))
        self.test_thread.stop()

    def test_loop_tick_tock_exception_stoppable_thread(self):
        self.test_thread = TestExceptionLoopThread()
        self.test_thread.start()
        self.assertTrue(work_done.acquire(True, TIMEOUT))
        self.test_thread.tock()
        self.assertTrue(work_done.acquire(True, TIMEOUT))
        self.test_thread.stop()

    def test_loop_sleep_thread(self):
        self.test_thread = TestLoopSleepThread()
        self.assertRaises(NotRunningException, self.test_thread.stop)
        self.test_thread.start()
        self.assertRaises(AlreadyRunningException, self.test_thread.start)
        self.test_thread.stop()

    def test_empty(self):
        self.test_thread = StoppableThread()
        self.test_thread.start()
        self.test_thread.stop()
        self.assertTrue(isinstance(logged_exceptions.pop(), NoWorkException))
