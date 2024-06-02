# Plex API
import os

from workers.watching_listener import WatchingListener
from workers.watchlist_listener import WatchlistScrapper
from utils.folders import load_folders


def main():
    load_folders()

    watchlist_scrapper = WatchlistScrapper()
    watching_listener = WatchingListener()

    watchlist_scrapper.start()
    watching_listener.start()

    start_django()

    watchlist_scrapper.stop()
    watching_listener.stop()


def start_django():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webui.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(["main.py", "runserver"])


if __name__ == "__main__":
    main()
