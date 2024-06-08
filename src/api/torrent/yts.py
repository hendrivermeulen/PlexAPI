import string

from selenium.webdriver.common.by import By

from api.torrent.torrent_browser import TorrentBrowser
from utils.logger import log
from utils.utils import parse_for_url


def extract(keyword, links):
    sources = []
    for link in links:
        link_title = link.get_attribute("title")
        link_href = link.get_attribute("href")
        if keyword in link_title and " Torrent" in link_title and "/torrent/download/" in link_href:
            if link_href not in sources:
                log("YTS Found " + link_title.replace("Download ", "").replace(" Torrent", ""))
                sources.append(link_href)
    return sources


class YTSTorrentBrowser(TorrentBrowser):

    def movie_search(self, title: string):
        return self.yts_direct_movie_query(title)

    def series_search(self, title: string):
        raise Exception("Not supported")

    def yts_direct_movie_query(self, title: string) -> []:
        try:
            query = "https://yts.mx/movies/" + parse_for_url(title)
            # Navigate to a website
            log("YTS search: " + query)
            self.driver.get(query)
            # Get results
            movie_info = self.driver.find_element(by=By.ID, value="movie-info")
            links = movie_info.find_elements(by=By.TAG_NAME, value="a")
            # sort results
            sources = []
            sources += extract("2160p", links)
            sources += extract("1080p", links)
            sources += extract("720p", links)
            return sources
        except:
            return []
