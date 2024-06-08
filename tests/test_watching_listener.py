import threading
from unittest import TestCase
from unittest.mock import MagicMock

from test_api import TestAPI
from workers.watching_listener import WatchingListener, WatchingNotifier


class TestWatchingNotifier(TestCase, WatchingListener):

    def setUp(self):
        self.started_playing_lock = threading.Semaphore(0)
        self.stopped_playing_lock = threading.Semaphore(0)
        self.playing = None
        self.stopped = None

        self.notifier = WatchingNotifier(self)
        self.notifier.plex_api.get_plex_connection = MagicMock(return_value=TestAPI())
        self.notifier.start()

    def tearDown(self):
        self.notifier.stop()

    def started_playing(self, item):
        self.playing = item
        self.started_playing_lock.release()

    def stopped_playing(self, item):
        self.stopped = item
        self.stopped_playing_lock.release()

    def test_listener(self):
        self.assertTrue(self.started_playing_lock.acquire(True, 5))
        self.assertEqual("Spider-man 2003", self.playing)

        self.assertTrue(self.stopped_playing_lock.acquire(True, 5))
        self.assertEqual("Spider-man 2003", self.stopped)
