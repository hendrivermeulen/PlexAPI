from api.qtorrent import QTorrentAPI
from utils.logger import log
from workers.watchlist_scrapper import VideoItem


# TODO convert to StoppableThread with priority queue and pause ability

def _add_torrent(qtorrent: QTorrentAPI, magnet: str, video_item: VideoItem, sleep_func: callable):
    qtorrent.repeat_until_process(
        lambda: qtorrent.add_torrent(magnet, video_item.is_movie, video_item.title), sleep_func)


def find_streamable(video_item: VideoItem, magnets: list[str], qtorrent: QTorrentAPI, sleep_func: callable):
    for magnet in magnets:
        _add_torrent(qtorrent, magnet, video_item, sleep_func)

        count = 0
        prev_eta = 100 * 365 * 24 * 3600  # 100 years

        is_streamable = False
        while count < 5:
            eta = qtorrent.repeat_until_process(lambda: qtorrent.get_torrent_eta(video_item.title), sleep_func)
            if eta < video_item.duration_s * 0.70:
                is_streamable = True
                break
            sleep_func(3) # TODO why is this not being stopped?
            if eta / prev_eta < 0.8:
                log("Speeding up")
                count = 0
            else:
                log("Too slow")
                count += 1
            prev_eta = eta

        if is_streamable:
            return True
        else:
            qtorrent.repeat_until_process(lambda: qtorrent.delete_torrent(video_item.title), sleep_func)
    return False
