import string
from enum import Enum

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import unittest

from src.api.utils import contains_title, parse_for_url


class TYPE(Enum):
    MOVIE = "207"
    SERIES = "208"


class TorrentBrowser:
    def __init__(self):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def movie_search(self, title: string):
        results = self.pirate_search(title, TYPE.MOVIE) + self.yts_direct_movie_query(title)
        results = list(dict.fromkeys(results))
        print("Found:", len(results))
        return results

    def series_search(self, title: string):
        return self.pirate_search(title, TYPE.SERIES)

    def pirate_search(self, title: string, cat: string):
        if cat == TYPE.MOVIE:
            urls = self.pirate_search_for_movie_url(title)
        else:
            urls = self.pirate_search_for_series_url(title)

        magnets = []
        for url in urls:
            self.driver.get(url)
            frame = self.driver.find_element(by=By.ID, value="details")
            div = frame.find_element(by=By.CLASS_NAME, value="download")
            link = div.find_element(by=By.TAG_NAME, value="a")
            magnet = link.get_attribute("href")
            if magnet not in magnets:
                print("Found", url)
                magnets.append(magnet)

        return magnets

    def pirate_search_for_movie_url(self, title: string):
        sources = []

        cat = TYPE.MOVIE.value
        # large
        atmos4k = self.pirate_query(title, cat, "Atmos 2160p HDR", 20, 30, 15)
        if atmos4k:
            sources.append(atmos4k)

        hdr4k = self.pirate_query(title, cat, "2160p HDR", 20, 30, 15)
        if hdr4k:
            sources.append(hdr4k)

        # small
        atmos4k = self.pirate_query(title, cat, "Atmos 2160p HDR", 20, 30, 8)
        if atmos4k:
            sources.append(atmos4k)

        hdr4k = self.pirate_query(title, cat, "2160p HDR", 20, 30, 8)
        if hdr4k:
            sources.append(hdr4k)

        return sources

    def pirate_search_for_series_url(self, title: string):
        cat = TYPE.SERIES.value
        # large
        atmos4k = self.pirate_query(title, cat, "Atmos 2160p HDR", 20, 30, 15)
        if atmos4k:
            return atmos4k

        hdr4k = self.pirate_query(title, cat, "2160p HDR", 20, 30, 15)
        if hdr4k:
            return hdr4k

        # small
        atmos4k = self.pirate_query(title, cat, "Atmos 2160p HDR", 20, 30, 8)
        if atmos4k:
            return atmos4k

        hdr4k = self.pirate_query(title, cat, "2160p HDR", 20, 30, 8)
        if hdr4k:
            return hdr4k

    def get_size(self, size_string):
        info = size_string.split(" ")
        if len(info) == 2 and info[1] == "GiB":
            return float(info[0])
        return 0.0

    def pirate_query(self, title: string, cat: string, quality: string, min_seed: int, max_size: float,
                     min_size: float):
        title += " " + quality
        query = "https://thepiratebay.party/search/" + title + "/1/99/" + cat
        query = query.replace(" ", "%20")
        # Navigate to a website
        print(query)
        self.driver.get(query)
        # Print the page title
        results = self.driver.find_element(by=By.ID, value="searchResult").find_elements(by=By.TAG_NAME, value="tr")

        for result in results[1:]:  # skip first as that is header
            info = result.find_elements(by=By.TAG_NAME, value="td")
            link = info[1].find_element(by=By.TAG_NAME, value="a")
            name = link.get_attribute("innerHTML").lower()
            seeds = int(info[5].text)
            size = self.get_size(info[4].text)

            if "cam" in name or "hdts" in name or "hd ts" in name:
                continue

            if seeds < min_seed:
                return None

            if max_size < size < min_size:
                continue

            if contains_title(title, name):
                return link.get_attribute("href")
            else:
                continue

        return None

    def extract(self, keyword, links):
        sources = []
        for link in links:
            link_title = link.get_attribute("title")
            link_href = link.get_attribute("href")
            if keyword in link_title and " Torrent" in link_title and "/torrent/download/" in link_href:
                if link_href not in sources:
                    print("Found", link_title)
                    sources.append(link_href)
        return sources

    def yts_direct_movie_query(self, title: string) -> []:
        try:
            query = "https://yts.mx/movies/" + parse_for_url(title)
            # Navigate to a website
            print(query)
            self.driver.get(query)
            # Get results
            movie_info = self.driver.find_element(by=By.ID, value="movie-info")
            links = movie_info.find_elements(by=By.TAG_NAME, value="a")
            # sort results
            sources = []
            sources += self.extract("2160p", links)
            sources += self.extract("1080p", links)
            sources += self.extract("720p", links)
            return sources
        except:
            return []


class TorrentBrowserTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = TorrentBrowser()

    def test_get_size(self):
        self.assertEqual(self.api.get_size("21.6 GiB"), 21.6)
        self.assertEqual(self.api.get_size("21.6 Gi"), 0.0)
        self.assertEqual(self.api.get_size("21.6 MiB"), 0.0)
