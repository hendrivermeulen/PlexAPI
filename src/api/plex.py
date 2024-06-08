import os

from plexapi.server import PlexServer
from dotenv import load_dotenv

from api.api import API

is_connected = False


class PlexAPI(API):
    def __init__(self):
        super().__init__("Plex")

        if not load_dotenv():
            raise RuntimeError("Could not load environmental variables from .env file")

        self.plex_url = os.environ.get("PLEX_URL")
        self.plex_token = os.environ.get("PLEX_TOKEN")

    def get_connection(self):
        return PlexServer(self.plex_url, self.plex_token)

    def get_watchlist(self) -> list:
        return self.confirm_connection(lambda: self._api.myPlexAccount().watchlist())

    def get_movies(self):
        return self.confirm_connection(lambda: self._api.library.section('Movies'))

    def get_series(self):
        return self.confirm_connection(lambda: self._api.library.section('TV Shows'))

    def get_name(self, item):
        return item.title + " " + str(item.year)

    def get_sessions(self):
        return self.confirm_connection(lambda: self._api.sessions())

    def start_alert_listener(self, listen):
        return self.confirm_connection(lambda: self._api.startAlertListener(listen))
