import datetime
import os
import string
import time
import traceback

import ffmpeg
import qbittorrentapi

from api.plex import PlexAPI
from utils.stoppable_thread import StoppableThread
from utils.utils import contains_at_least_half


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
            pass

class QTorrentAPI(StoppableThread):
    def __init__(self, plex_api: PlexAPI):
        super().__init__()
        self.plex_api = plex_api
        # instantiate a Client using the appropriate WebUI configuration
        conn_info = dict(
            host=os.environ.get("QBITTORRENT_HOST"),
            port=os.environ.get("QBITTORRENT_PORT"),
            username=os.environ.get("QBITTORRENT_USERNAME"),
            password=os.environ.get("QBITTORRENT_PASSWORD"),
        )
        self.client = qbittorrentapi.Client(**conn_info)

    def run(self):
        while True:
            try:
                self.housekeeping()
                time.sleep(60)
            except:
                traceback.print_exc()

    def pause_torrent(self, torrent_hash, title):
        print("Torrent paused", title)
        self.client.torrents_pause(torrent_hashes=torrent_hash)

    def stream_torrent(self, is_movie: bool, item):
        print("Looking for", item.title)
        for torrent in self.client.torrents_info():
            if contains_at_least_half(item.title, torrent.name):
                self.client.torrents_resume(torrent_hashes=torrent.hash)
                print("Torrent resumed", item.title)
                return torrent.hash

        save_path = self.plex_api.library_path
        if is_movie:
            save_path += "Movies"
        else:
            save_path += "TV-Shows"

        save_path += "/" + self.plex_api.get_name(item)
        torrent_src_file = open(save_path + "/magnet", "r")
        magnet = torrent_src_file.read()
        torrent_src_file.close()

        if magnet is not None:
            print("Stored Magnet Found")
            self.client.torrents_add(
                urls=magnet, is_sequential_download=True, save_path=save_path)
        else:
            print("Could not find magnet for playing item")
            return None

        attempts = 0
        while True:
            for torrent in self.client.torrents_info():
                if contains_at_least_half(item.title, torrent.name):
                    print("Torrent started")
                    return torrent.hash

            attempts += 1
            if attempts > 5:
                print("Magnet was never added")
                return None

            time.sleep(1)

    def add_torrent(self, magnet, is_movie: bool, title: string, duration_s):
        save_path = self.plex_api.library_path
        if is_movie:
            save_path += "Movies"
        else:
            save_path += "TV-Shows"
        save_path += "/" + title
        self.client.torrents_add(
            urls=magnet, is_sequential_download=True, save_path=save_path)

        attempts = 0
        while True:
            for torrent in self.client.torrents_info():
                if contains_at_least_half(title, torrent.name):
                    count = 0
                    prev_eta = 100 * 365 * 24 * 3600  # 100 years
                    is_streamable = False
                    while count < 5:
                        info = self.client.torrents_info(torrent_hashes=torrent.hash)[0]
                        eta = info['eta']
                        if eta < duration_s*0.70:
                            is_streamable = True
                            break
                        time.sleep(3)
                        if eta / prev_eta < 0.8:
                            print("Speeding up")
                            count = 0
                        else:
                            print("Too slow")
                            count += 1
                        prev_eta = eta

                    if is_streamable:
                        torrent_src_file = open(save_path + "/magnet", "w")
                        torrent_src_file.write(magnet)
                        torrent_src_file.close()
                    else:
                        self.client.torrents_delete(delete_files=True, torrent_hashes=torrent.hash)

                    return is_streamable

            attempts += 1
            if attempts > 5:
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
