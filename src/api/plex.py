import os

from plexapi.server import PlexServer
from dotenv import load_dotenv


class PlexAPI:
    def __init__(self):
        if not load_dotenv():
            raise Exception("Could not load environmental variables from .env file")

        plex_url = os.environ.get("PLEX_URL")
        plex_token = os.environ.get("PLEX_TOKEN")

        self.server = PlexServer(plex_url, plex_token)

    def get_watchlist(self) -> list:
        return self.server.myPlexAccount().watchlist()

    def get_movies(self):
        return self.server.library.section('Movies')

    def get_series(self):
        return self.server.library.section('TV Shows')

    def get_name(self, item):
        return item.title + " " + str(item.year)
