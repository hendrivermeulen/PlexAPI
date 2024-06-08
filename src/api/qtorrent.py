import os
import string
import time

import ffmpeg
import qbittorrentapi
from qbittorrentapi import Client

from api.api import API
from utils.folders import library_path


def extract_task(from_file, to_file, secs):
    while True:
        try:
            (
                ffmpeg
                .input(from_file)
                .trim(start_frame=0, end_frame=24 * secs)
                .output(to_file)
                .overwrite_output()
                .run(quiet=True)
            )
            break
        except:
            time.sleep(secs / 2)


class QTorrentAPI(API):
    def __init__(self):
        super().__init__("QTorrent")
        # instantiate a Client using the appropriate WebUI configuration
        self.conn_info = dict(
            host=os.environ.get("QBITTORRENT_HOST"),
            port=os.environ.get("QBITTORRENT_PORT"),
            username=os.environ.get("QBITTORRENT_USERNAME"),
            password=os.environ.get("QBITTORRENT_PASSWORD"),
        )

        self._api: Client | None = None

    def get_connection(self):
        return qbittorrentapi.Client(**self.conn_info)

    def _pause_torrent(self, torrent_hash):
        self._api.torrents_pause(torrent_hashes=torrent_hash)
        return True

    def pause_torrent(self, title):
        return self.confirm_connection(lambda: self._pause_torrent(self._title_to_hash(title)))

    def _resume_torrent(self, torrent_hash):
        self._api.torrents_resume(torrent_hashes=torrent_hash)
        return True

    def resume_torrent(self, title):
        return self.confirm_connection(lambda: self._resume_torrent(self._title_to_hash(title)))

    def _add_torrent(self, magnet: str, is_movie: bool, title: string):
        save_path = library_path
        if is_movie:
            save_path += "Movies"
        else:
            save_path += "TV-Shows"
        save_path += "/" + title
        self._api.torrents_add(
            urls=magnet, is_sequential_download=True, save_path=save_path, tags=title)
        return True

    def add_torrent(self, magnet, is_movie: bool, title: string):
        return self.confirm_connection(lambda: self._add_torrent(magnet, is_movie, title))

    def _title_to_hash(self, title):
        for torrent in self._api.torrents_info(tag=title):
            return torrent.hash

    def _get_torrent_eta(self, title):
        for torrent in self._api.torrents_info(tag=title):
            return torrent["eta"]
        return None

    def get_torrent_eta(self, title):
        return self.confirm_connection(lambda: self._get_torrent_eta(title))

    def _delete_torrent(self, torrent_hash):
        self._api.torrents_delete(delete_files=True, torrent_hashes=torrent_hash)
        return True

    def delete_torrent(self, title):
        return self.confirm_connection(lambda: self._delete_torrent(self._title_to_hash(title)))
