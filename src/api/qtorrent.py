import datetime
import os
import string
import time
import traceback
from threading import Thread

import ffmpeg
import qbittorrentapi

from src.api.plex import PlexAPI
from src.api.utils import contains_at_least_half


class QTorrentAPI(Thread):
    def __init__(self, plex_api: PlexAPI):
        super().__init__()
        self.plex_api = plex_api
        # instantiate a Client using the appropriate WebUI configuration
        conn_info = dict(
            host="localhost",
            port=8080,
            username="admin",
            password="adminadmin",
        )
        self.client = qbittorrentapi.Client(**conn_info)
        self.library_path = "/var/lib/plexmediaserver/Library/"

    def run(self):
        while True:
            try:
                self.housekeeping()
                time.sleep(60)
            except:
                traceback.print_exc()

    def add_torrent(self, magnet, is_movie: bool, title: string, id):
        temp_path = self.library_path + "temp/"
        save_path = self.library_path
        if is_movie:
            save_path += "Movies"
        else:
            save_path += "TV-Shows"
        self.client.torrents_add(
            urls=magnet, is_sequential_download=True, save_path=temp_path)

        found = False
        while not found:
            for torrent in self.client.torrents_info():
                if contains_at_least_half(title, torrent.name):
                    required_bytes = 0
                    while True:
                        info = self.client.torrents_properties(torrent.hash)
                        total_downloaded = info["total_downloaded"]
                        if total_downloaded > required_bytes:
                            break
                        time.sleep(0.1)
                    files = self.client.torrents_files(torrent.hash)
                    max_size = -1
                    biggest_file = None

                    for file in files:
                        if biggest_file is None or file["size"] > max_size:
                            max_size = file["size"]
                            biggest_file = file

                    biggest_file_name_with_extension = os.path.basename(biggest_file["name"])
                    biggest_file_name_without_extension = biggest_file_name_with_extension[0:biggest_file_name_with_extension.rindex(".")]

                    fake_file_folder = save_path + "/" + title + "/" + biggest_file_name_without_extension + "-FAKE"
                    fake_file = fake_file_folder + "/" + biggest_file_name_with_extension
                    os.makedirs(fake_file_folder, exist_ok=True)

                    real_file = temp_path + biggest_file["name"]
                    self.extract(real_file, fake_file, id)

                    self.client.torrents_delete(delete_files=True, torrent_hashes=torrent.hash)
                    found = True
                    break
            time.sleep(0.1)

    def get_torrents(self):
        return self.client.torrents_info()

    def housekeeping(self):
        for torrent in self.client.torrents_info():
            # clean
            no_longer_needed = True
            for item in self.plex_api.get_watchlist():
                if contains_at_least_half(self.plex_api.get_name(item), torrent.name):
                    if item.lastViewedAt is None:
                        no_longer_needed = False
                    else:
                        last_viewed_days = (datetime.datetime.now() - item.lastViewedAt).days
                        no_longer_needed = item.viewCount != 0 and last_viewed_days >= 0
                    break

            if no_longer_needed:
                self.client.torrents_delete(True, torrent.hash)

    def extract(self, from_file, to_file, secs):
        print(secs)
        while True:
            try:
                (
                    ffmpeg
                    .input(from_file)
                    .trim(start_frame=0, end_frame=24*secs)
                    .output(to_file)
                    .run(overwrite_output=True, quiet=True)
                 )
                break
            except:
                time.sleep(0.1)

if __name__ == "__main__":
    api = QTorrentAPI(None)
    print(api.get_torrents()[0])
