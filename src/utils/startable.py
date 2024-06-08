class Startable:

    def __init__(self):
        self.is_running = False

    def start(self):
        if self.is_running:
            raise AlreadyRunningException()
        else:
            self.is_running = True
            self.on_start()

    def stop(self):
        if self.is_running:
            self.is_running = False
            self.on_stop()
        else:
            raise NotRunningException()

    def on_start(self):
        pass

    def on_stop(self):
        pass


class NotRunningException(Exception):
    pass


class AlreadyRunningException(Exception):
    pass
