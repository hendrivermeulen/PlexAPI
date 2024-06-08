from unittest import TestCase

from api.torrent_api import TorrentAPI
from utils.logger import logged_messages

MOVIE = "The Fall Guy"
YEAR = "2024"


class TestTorrentAPI(TestCase):
    def test_movie_search(self):
        torrent_api = TorrentAPI()
        torrent_list = torrent_api.movie_search(MOVIE + " " + YEAR)
        self.assertTrue(len(torrent_list) > 0)

        self.assertTrue("Pirate Bay Found " + MOVIE + " " + YEAR + " Atmos 2160p HDR" in logged_messages)
        self.assertTrue("YTS Found " + MOVIE + " 2160p" in logged_messages)
        self.assertTrue("YTS Found " + MOVIE + " 1080p" in logged_messages)
        self.assertTrue("YTS Found " + MOVIE + " 720p" in logged_messages)

        self.assertTrue(len(torrent_list) > 0)

    def test_series_search(self):
        pass
