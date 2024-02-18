import datetime
import os
import shutil
import string
import threading
import time
import traceback
from threading import Thread

import ffmpeg
import qbittorrentapi

from src.api.plex import PlexAPI
from src.api.utils import contains_at_least_half

extract_waiting_lock = threading.Semaphore(0)


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
            time.sleep(secs/2)
            pass
    extract_waiting_lock.release(1)


def extract(from_file, to_file, secs, timeout):
    thread = threading.Thread(target=extract_task, args=[from_file, to_file, secs])
    thread.start()
    return extract_waiting_lock.acquire(timeout=timeout)


def check_streamable(from_file, to_file, secs):
    init_time = 1
    expected = secs/1.5
    # wait to start
    if not extract(from_file, to_file, init_time, 5):
        print("Initialization timeout")
        return False
    # extract
    if not extract(from_file, to_file, secs + init_time, expected):
        os.system("pkill ffmpeg")
        os.remove(to_file)
        print("Not keeping up")
        return False
    return True


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

    def run(self):
        while True:
            try:
                self.housekeeping()
                time.sleep(60)
            except:
                traceback.print_exc()

    def pause_torrent(self, hash):
        print("Torrent paused")
        self.client.torrents_pause(torrent_hashes=hash)

    def stream_torrent(self, is_movie: bool, title: string):
        save_path = self.plex_api.library_path
        if is_movie:
            save_path += "Movies"
        else:
            save_path += "TV-Shows"

        save_path += "/" + title
        torrent_src_file = open(save_path + "/magnet", "r")
        magnet = torrent_src_file.read()
        torrent_src_file.close()

        for torrent in self.client.torrents_info():
            if contains_at_least_half(title, torrent.name):
                self.client.torrents_resume(torrent_hashes=torrent.hash)
                print("Torrent resumed")
                return torrent.hash

        if magnet is not None:
            print("Stored Magnet Found")
            self.client.torrents_add(
                urls=magnet, is_sequential_download=True, save_path=save_path)
        else:
            print("Could not find magnet for playing item")

        attempts = 0
        while True:
            for torrent in self.client.torrents_info():
                if contains_at_least_half(title, torrent.name):
                    print("Torrent started")
                    return torrent.hash

            attempts += 1
            if attempts > 3:  # after 3 seconds of trying
                print("Magnet was never added")
                return None

            time.sleep(1)


    def add_torrent(self, magnet, is_movie: bool, title: string):
        temp_path = self.plex_api.library_path + "temp/"
        save_path = self.plex_api.library_path
        if is_movie:
            save_path += "Movies"
        else:
            save_path += "TV-Shows"
        self.client.torrents_add(
            urls=magnet, is_sequential_download=True, save_path=temp_path)

        attempts = 0
        while True:
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
                    download_folder = os.path.dirname(biggest_file["name"])

                    fake_file_base_folder = save_path + "/" + title
                    fake_file_folder = fake_file_base_folder + "/" + download_folder
                    fake_file = fake_file_folder + "/" + biggest_file_name_with_extension
                    os.makedirs(fake_file_folder, exist_ok=True)

                    real_file = temp_path + biggest_file["name"]
                    is_streamable = check_streamable(real_file, fake_file, 5)

                    # clean up qTorrent
                    self.client.torrents_delete(delete_files=True, torrent_hashes=torrent.hash)

                    if is_streamable:
                        # safe
                        torrent_src_file = open(fake_file_base_folder + "/magnet", "w")
                        torrent_src_file.write(magnet)
                        torrent_src_file.close()
                    else:
                        # clean up
                        shutil.rmtree(fake_file_base_folder)

                    return is_streamable

            attempts += 1
            if attempts > 3:  # after 3 seconds of trying
                print("Magnet was never added")
                break

            time.sleep(1)

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
