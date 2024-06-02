import os

from plexapi.server import PlexServer
from dotenv import load_dotenv

from utils.startable import Startable


class PlexAPI(Startable):
    def __init__(self):
        super().__init__()

        if not load_dotenv():
            raise Exception("Could not load environmental variables from .env file")

        self.plex_url = os.environ.get("PLEX_URL")
        self.plex_token = os.environ.get("PLEX_TOKEN")
        self.library_path = os.environ.get("PLEX_LIBRARY_PATH")  # TODO replace with folders

        self.server = None

    def on_start(self):
        self.server = PlexServer(self.plex_url, self.plex_token)

    def get_watchlist(self) -> list:
        return self.server.myPlexAccount().watchlist()

    def get_movies(self):
        return self.server.library.section('Movies')

    def get_series(self):
        return self.server.library.section('TV Shows')

    def get_name(self, item):
        return item.title + " " + str(item.year)
