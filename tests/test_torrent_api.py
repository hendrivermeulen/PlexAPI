from unittest import TestCase

from api.torrent_api import TorrentAPI
from utils.logger import logged_messages

MOVIE = "The Fall Guy"
YEAR = "2024"


class TestTorrentAPI(TestCase):

    def setUp(self):
        self.torrent_api = TorrentAPI()
        self.torrent_api.start()

    def tearDown(self):
        self.torrent_api.stop()

    def test_movie_search(self):
        torrent_list = self.torrent_api.movie_search(MOVIE + " " + YEAR)
        self.assertGreater(len(torrent_list), 0)

        self.assertIn("Pirate Bay Found " + MOVIE + " " + YEAR + " Atmos 2160p HDR", logged_messages)
        self.assertIn("YTS Found " + MOVIE + " 2160p", logged_messages)
        self.assertIn("YTS Found " + MOVIE + " 1080p", logged_messages)
        self.assertIn("YTS Found " + MOVIE + " 720p", logged_messages)
        self.assertGreaterEqual(len(torrent_list), 4)

    def test_no_movie_found(self):
        self.assertEqual(0, len(self.torrent_api.movie_search("This movie does not exist")))

    def test_series_search(self):
        pass
