class Startable:

    def __init__(self):
        self.is_running = False

    def start(self):
        if self.is_running:
            raise AlreadyRunningException()
        else:
            self.is_running = True
            self.on_start()
            self.started()

    def started(self):
        pass

    def stop(self):
        if self.is_running:
            self.is_running = False
            self.on_stop()
            self.stopped()
        else:
            raise NotRunningException()

    def stopped(self):
        pass

    def on_start(self):
        pass

    def on_stop(self):
        pass


class NotRunningException(Exception):
    pass


class AlreadyRunningException(Exception):
    pass
