from utils.stoppable_thread import StoppableThread


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


class AlertListener(StoppableThread):

    def __init__(self, listen: callable):
        super().__init__("TestAPIAlertListener")
        self.listen = listen

    def work(self):
        self.listen({
            "type": "playing",
            "PlaySessionStateNotification": [{"state": "playing"}]
        })

        self.listen({
            "type": "playing",
            "PlaySessionStateNotification": [{"state": "stopped"}]
        })


class TestAPI:
    def sessions(self):
        return [[Item("Spider-man", 2003)]]

    def myPlexAccount(self):
        return MyPlexAccount()

    def startAlertListener(self, listen: callable):
        listener = AlertListener(listen)
        listener.start()
        return listener
