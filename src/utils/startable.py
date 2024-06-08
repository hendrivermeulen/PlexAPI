import threading


class Startable:

    def __init__(self):
        self._is_running = False
        self._is_running_lock = threading.Lock()

    def start(self):
        if self.is_running():
            raise AlreadyRunningException()
        else:
            with self._is_running_lock:
                self._is_running = True
            self.on_start()

    def stop(self):
        if self.is_running():
            with self._is_running_lock:
                self._is_running = False
            self.on_stop()
        else:
            raise NotRunningException()

    def is_running(self):
        with self._is_running_lock:
            return self._is_running

    def on_start(self):
        # optional
        pass

    def on_stop(self):
        # optional
        pass


class NotRunningException(Exception):
    pass


class AlreadyRunningException(Exception):
    pass
