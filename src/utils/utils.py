import re
import string
import time
import unittest


def remove_non_alpha(text: string):
    pattern = re.compile('[\W]+')
    return pattern.sub('', text)


def parse_for_url(text: string):
    pattern = re.compile('[^\w\s-]+')
    result = pattern.sub('', text).lower()
    pattern = re.compile('[\s]+')
    result = pattern.sub('-', result)
    pattern = re.compile('-+')
    result = pattern.sub('-', result)
    return result


def contains_title(title: string, name: string):
    tokens = title.lower().split(" ")
    name = name.lower()
    name = remove_non_alpha(name)
    for token in tokens:
        token = token.strip()
        token = remove_non_alpha(token)
        if token not in name:
            return False
    return True


def contains_at_least_half(title: string, name: string):
    tokens = title.lower().split(" ")
    name = name.lower()
    name = remove_non_alpha(name)

    count = 0
    for token in tokens:
        token = token.strip()
        token = remove_non_alpha(token)
        if token in name:
            count += 1

    contains = count / len(tokens) >= 0.5
    return contains


def await_value(call: callable, value, timeout_ms: int):
    time_slept_ms = 0
    while not call() == value:
        time.sleep(0.1)
        time_slept_ms += 100
        if time_slept_ms >= timeout_ms:
            return False
    return True
