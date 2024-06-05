from unittest import TestCase
from unittest.mock import MagicMock

from test_api import Item, TestAPI
from utils.utils import await_value
from workers.main_worker import MainWorker
from workers.watchlist_scrapper import WatchlistScrapper

TIMEOUT_MS = 3000


class TestWatchlistScrapper(TestCase):

    def setUp(self):
        self.worker = MainWorker()

        self.added_mock = MagicMock()
        self.removed_mock = MagicMock()

        self.worker.watchlist_item_added = self.added_mock
        self.worker.watchlist_item_removed = self.removed_mock

        self.scrapper = WatchlistScrapper([], self.worker)
        self.scrapper.plex_api.get_plex_connection = MagicMock(return_value=TestAPI())
        self.scrapper.plex_api.get_watchlist = MagicMock(return_value=[
            Item("Spider-man", 2003),
            Item("Spider-man", 2005),
            Item("Spider-man", 2007)
        ]) # TODO use TestAPI

        self.scrapper.start()

    def tearDown(self):
        self.scrapper.stop()

    def test(self):
        # new items
        self.assertTrue(await_value(lambda: self.added_mock.call_count, 3, TIMEOUT_MS))
        self.assertEqual(["Spider-man 2003", "Spider-man 2005", "Spider-man 2007"], self.scrapper.watchlist)

        self.scrapper.plex_api.get_watchlist = MagicMock(return_value=[
            Item("Spider-man", 2003),
        ])
        # remove old
        self.assertTrue(await_value(lambda: self.removed_mock.call_count, 2, TIMEOUT_MS))
        self.assertEqual(["Spider-man 2003"], self.scrapper.watchlist)

        self.scrapper.plex_api.get_watchlist = MagicMock(return_value=[
            Item("Ironman", 2003),
        ])
        self.assertTrue(await_value(lambda: self.removed_mock.call_count, 3, TIMEOUT_MS))
        self.assertTrue(await_value(lambda: self.added_mock.call_count, 4, TIMEOUT_MS))
        self.assertEqual(["Ironman 2003"], self.scrapper.watchlist)

        # confirm calls
        self.added_mock.assert_any_call("Spider-man 2003")
        self.added_mock.assert_any_call("Spider-man 2005")
        self.added_mock.assert_any_call("Spider-man 2007")
        self.added_mock.assert_any_call("Ironman 2003")

        self.removed_mock.assert_any_call("Spider-man 2003")
        self.removed_mock.assert_any_call("Spider-man 2005")
        self.removed_mock.assert_any_call("Spider-man 2007")

        # still the same
        self.assertTrue(await_value(lambda: self.added_mock.call_count, 4, 1000))
        self.assertTrue(await_value(lambda: self.removed_mock.call_count, 3, 1000))
        self.assertEqual(["Ironman 2003"], self.scrapper.watchlist)



