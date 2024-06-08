import threading
from unittest import TestCase
from unittest.mock import MagicMock, Mock
from test_api import TestAPI, connection_called, has_connection_called
from utils.utils import await_value
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

    def test_default_listener(self):
        listener = WatchingListener()
        self.assertRaises(NotImplementedError, lambda: listener.started_playing(""))
        self.assertRaises(NotImplementedError, lambda: listener.stopped_playing(""))

    def testNoConnection(self):
        self.notifier.stop()
        mock = Mock(side_effect=connection_called)
        self.notifier.plex_api.get_plex_connection = mock
        self.notifier.start()
        self.assertTrue(await_value(has_connection_called, True, 10000))
