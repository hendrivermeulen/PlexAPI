from unittest import TestCase
from unittest.mock import MagicMock

from utils.startable import Startable, NotRunningException, AlreadyRunningException


class TestStartable(TestCase):
    def test(self):
        startable = Startable()
        self.assertRaises(NotRunningException, startable.stop)
        startable.start()
        self.assertRaises(AlreadyRunningException, startable.start)
        startable.stop()

        started_mock = MagicMock()
        startable.on_start = started_mock

        stopped_mock = MagicMock()
        startable.on_stop = stopped_mock

        startable.start()
        started_mock.assert_called()
        startable.stop()
        stopped_mock.assert_called()
