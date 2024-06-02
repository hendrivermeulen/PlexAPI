import sys


logged_exceptions: list = []


def log(message: str = None, exception: Exception = None):
    if message is not None:
        print(message, file=sys.stderr)
    else:
        logged_exceptions.append(exception)
        print(exception, file=sys.stderr)


class NoException(Exception):
    pass
