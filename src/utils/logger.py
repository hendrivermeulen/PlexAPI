import sys
import threading
import traceback

logged_exceptions: list = []
logged_messages: list = []
logging_lock = threading.Lock()


def log_error(message: str):
    print(message, file=sys.stderr)


def log(message: str = None, exception: Exception = None):
    with logging_lock:
        if message is not None:
            if exception is None:
                print(message)
                logged_messages.append(message)
            else:
                print(message, file=sys.stderr)
        else:
            if exception is not None:
                logged_exceptions.append(exception)
                print(exception, file=sys.stderr)
                print(traceback.format_exc(), file=sys.stderr)


class NoException(Exception):
    pass
