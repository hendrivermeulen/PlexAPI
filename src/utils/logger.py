import sys


def log(message: str = None, exception: Exception = None):
    if message is not None:
        print(message, file=sys.stderr)
    print(exception)


class NoException(Exception):
    pass
