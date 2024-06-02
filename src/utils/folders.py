import os
from os.path import exists

library_path = os.environ.get("PLEX_LIBRARY_PATH")
series_path = os.path.join(library_path, "TV-Shows")
movies_path = os.path.join(library_path, "Movies")


def load_folders():
    if exists(library_path):
        os.makedirs(series_path, exist_ok=True)
        os.makedirs(movies_path, exist_ok=True)
    else:
        raise Exception("Library path does not exist ", library_path)