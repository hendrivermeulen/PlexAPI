# Plex API
from src.api.watching import WatchingListener
from src.api.watchlist import WatchlistScrapper

if __name__ == "__main__":
    WatchlistScrapper().start()
    WatchingListener().start()
