class Item:

    def __init__(self, title, year):
        self.title = title
        self.year = year


class MyPlexAccount:
    def get_watchlist(self):
        return [
            Item("Spider-man", 2003),
            Item("Spider-man", 2005),
            Item("Spider-man", 2007)
        ]


class TestAPI:
    def sessions(self):
        return [[Item("Spider-man", 2003)]]

    def myPlexAccount(self):
        return  MyPlexAccount()