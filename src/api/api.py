from utils.logger import log, log_error


def repeat_until_process(call: callable, sleep_func: callable):
    result = call()
    while result is None or result is False:
        result = call()
        sleep_func(3)
    return result


class API:

    def __init__(self, name: str):
        self._api = None
        self.name = name
        self._connected = False

    def get_connection(self):
        raise NotImplementedError()

    def confirm_connection(self, call: callable):
        try:
            self._api = self.get_connection()
            if not self._connected:
                self._connected = True
                log("Connected to " + self.name)

            if self._connected:
                return call()
            else:
                return None
        except Exception: # ConnectionError | ReadTimeout | APIConnectionError
            self._connected = False
            log_error("Lost connection to " + self.name)
            return None
