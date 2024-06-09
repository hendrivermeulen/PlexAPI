import os
from os.path import exists
from dotenv import load_dotenv

load_dotenv()

library_path = os.environ.get("PLEX_LIBRARY_PATH")
if library_path is None:
    raise RuntimeError("PLEX_LIBRARY_PATH not set")

series_path = os.path.join(library_path, "TV-Shows")
movies_path = os.path.join(library_path, "Movies")


def load_folders():
    if exists(library_path):
        os.makedirs(series_path, exist_ok=True)
        os.makedirs(movies_path, exist_ok=True)
    else:
        raise IOError("Library path does not exist ", library_path)


def get_save_path(is_movie: bool, title: str):
    if is_movie:
        return os.path.join(movies_path, title)
    else:
        return os.path.join(series_path, title)
