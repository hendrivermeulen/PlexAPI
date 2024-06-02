import threading
from unittest import TestCase

from utils.stoppable_thread import StoppableThread, StoppedException, StopTimeoutException

TIMEOUT = 10

work_done = threading.Semaphore(0)
stopped = threading.Semaphore(0)
stop = threading.Semaphore(0)


class TestThread(StoppableThread):

    def work(self):
        while self.running:
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
        super().__init__(should_loop=True, enable_tick_tock=True)

    def work(self):
        work_done.release(1)
        raise Exception("Test")


class LoopTestThread(StoppableThread):

    def __init__(self, enable_tick_tock=False):
        super().__init__(should_loop=True, enable_tick_tock=enable_tick_tock)

    def work(self):
        work_done.release(1)


class Test(TestCase):

    def test_stoppable_thread(self):
        try:
            test_thread = TestThread()
            test_thread.start()
            self.assertTrue(work_done.acquire(True, TIMEOUT))
            test_thread.stop()
            self.assertTrue(stopped.acquire(True, TIMEOUT))
        except Exception as e:
            self.fail(e)

    def test_unstoppable_thread(self):
        try:
            test_thread = TestUnstoppableThread()
            test_thread.start()
            self.assertRaises(StopTimeoutException, test_thread.stop)
            stop.release()
        except Exception as e:
            self.fail(e)

    def test_loop_stoppable_thread(self):
        try:
            test_thread = LoopTestThread()
            test_thread.start()
            self.assertTrue(work_done.acquire(True, TIMEOUT))
            test_thread.stop()
        except Exception as e:
            self.fail(e)

    def test_loop_tick_tock_stoppable_thread(self):
        try:
            test_thread = LoopTestThread(True)
            test_thread.start()
            self.assertTrue(work_done.acquire(True, TIMEOUT))
            test_thread.tock()
            self.assertTrue(work_done.acquire(True, TIMEOUT))
            test_thread.stop()
        except Exception as e:
            self.fail(e)

    def test_loop_tick_tock_exception_stoppable_thread(self):
        try:
            test_thread = TestExceptionLoopThread()
            test_thread.start()
            self.assertTrue(work_done.acquire(True, TIMEOUT))
            test_thread.tock()
            self.assertTrue(work_done.acquire(True, TIMEOUT))
            test_thread.stop()
        except Exception as e:
            self.fail(e)

    def test_loop_sleep_thread(self):
        try:
            test_thread = TestLoopSleepThread()
            test_thread.start()
            test_thread.stop()
        except Exception as e:
            self.fail(e)
