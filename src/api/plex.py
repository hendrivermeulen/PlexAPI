import os

from plexapi.server import PlexServer
from dotenv import load_dotenv

from utils.logger import log, log_error
from requests.exceptions import ConnectionError

is_connected = False


class PlexAPI:
    def __init__(self):
        super().__init__()

        if not load_dotenv():
            raise RuntimeError("Could not load environmental variables from .env file")

        self.plex_url = os.environ.get("PLEX_URL")
        self.plex_token = os.environ.get("PLEX_TOKEN")
        self.library_path = os.environ.get("PLEX_LIBRARY_PATH")  # TODO replace with folders

        self._server = None

    def get_plex_connection(self):
        return PlexServer(self.plex_url, self.plex_token)

    def confirm_connection(self, call: callable):
        global is_connected
        try:
            self._server = self.get_plex_connection()
            if not is_connected:
                is_connected = True
                log("Connected to Plex")
        except ConnectionError:
            is_connected = False
            log_error("Lost connection to Plex")

        if is_connected:
            return call()
        else:
            return None

    def get_watchlist(self) -> list:
        return self.confirm_connection(lambda: self._server.myPlexAccount().watchlist())

    def get_movies(self):
        return self.confirm_connection(lambda: self._server.library.section('Movies'))

    def get_series(self):
        return self.confirm_connection(lambda: self._server.library.section('TV Shows'))

    def get_name(self, item):
        return item.title + " " + str(item.year)

    def get_sessions(self):
        return self.confirm_connection(lambda: self._server.sessions())

    def start_alert_listener(self, listen):
        return self.confirm_connection(lambda: self._server.startAlertListener(listen))
