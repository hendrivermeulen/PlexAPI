import string
from enum import Enum

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from api.torrent.torrent_browser import TorrentBrowser, Quality, Result
from utils.logger import log
from utils.utils import contains_title


class TYPE(Enum):
    MOVIE = "211"
    SERIES = "208"


def get_size(size_string):
    info = size_string.split(" ")
    if len(info) == 2 and info[1] == "GiB":
        return float(info[0])
    return 0.0


def process(sources, results):
    if results:
        sources.append(results)


class PirateBayTorrentBrowser(TorrentBrowser):

    def movie_search(self, title: string):
        return self.pirate_search(title, TYPE.MOVIE)

    def series_search(self, title: string):
        return self.pirate_search(title, TYPE.SERIES)

    def pirate_search(self, title: string, cat: string):
        if cat == TYPE.MOVIE:
            results = self.pirate_search_for_movie_url(title)
        else:
            results = self.pirate_search_for_series_url(title)

        magnets = []
        final_results: list[Result] = []
        for result in results:
            self.driver.get(result.magnet)
            frame = self.driver.find_element(by=By.ID, value="details")
            div = frame.find_element(by=By.CLASS_NAME, value="download")
            link = div.find_element(by=By.TAG_NAME, value="a")
            magnet = link.get_attribute("href")
            if magnet not in magnets:
                result.magnet = magnet
                magnets.append(magnet)
                final_results.append(result)
                log("Pirate Bay Found " + title + " " + result.quality.value)

        return final_results

    def pirate_search_for_movie_url(self, title: string):
        sources = []

        cat = TYPE.MOVIE.value
        # large
        process(sources, self.pirate_query(title, cat, Quality.ATMOS_HDR, 20, 30, 15))
        process(sources, self.pirate_query(title, cat, Quality.HDR, 20, 30, 15))
        # small
        process(sources, self.pirate_query(title, cat, Quality.ATMOS_HDR, 20, 30, 8))
        process(sources, self.pirate_query(title, cat, Quality.HDR, 20, 30, 8))

        return sources

    def pirate_search_for_series_url(self, title: string):
        cat = TYPE.SERIES.value
        # large
        atmos4k = self.pirate_query(title, cat, Quality.ATMOS_HDR, 20, 30, 15)
        if atmos4k:
            return atmos4k

        hdr4k = self.pirate_query(title, cat, Quality.HDR, 20, 30, 15)
        if hdr4k:
            return hdr4k

        # small
        atmos4k = self.pirate_query(title, cat, Quality.ATMOS_HDR, 20, 30, 8)
        if atmos4k:
            return atmos4k

        hdr4k = self.pirate_query(title, cat, Quality.HDR, 20, 30, 8)
        if hdr4k:
            return hdr4k

    def pirate_query(self, title: string, cat: string, quality: Quality, min_seed: int, max_size: float,
                     min_size: float):
        try:
            title += " " + str(quality.value)
            query = "https://thepiratebay.party/search/" + title + "/1/99/" + cat
            query = query.replace(" ", "%20")
            # Navigate to a website
            log("Pirate search: " + query)
            self.driver.get(query)
            # Print the page title
            results = self.driver.find_element(by=By.ID, value="searchResult").find_elements(by=By.TAG_NAME, value="tr")

            for result in results[1:]:  # skip first as that is header
                info = result.find_elements(by=By.TAG_NAME, value="td")
                link = info[1].find_element(by=By.TAG_NAME, value="a")
                name = link.get_attribute("innerHTML").lower()
                seeds = int(info[5].text)
                size = get_size(info[4].text)

                if "cam" in name or "hdts" in name or "hd ts" in name:
                    continue

                if seeds < min_seed:
                    return None

                if max_size < size < min_size:
                    continue

                if contains_title(title, name):
                    return Result(link.get_attribute("href"), quality)
                else:
                    continue
        except NoSuchElementException:
            pass

        return None
