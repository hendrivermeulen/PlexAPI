import re
import string
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


class UtilsTest(unittest.TestCase):
    def test_contains_title(self):
        self.assertTrue(contains_title("Test 123", "Test 123"))
        self.assertTrue(contains_title("Test 123", "Extra Test 123 Extra"))
        self.assertTrue(contains_title("Test 123", "Extra.Test.123.Extra"))
        self.assertTrue(contains_title("Test-123", "Extra.Test-123.Extra"))

        self.assertTrue(contains_title("Mission: Impossible - Dead Reckoning Part One 1080p",
                                       "Mission Impossible - Dead Reckoning Part One (2023) [1080p] [WEBRip]"))

        self.assertFalse(contains_title("Test 123", ""))
        self.assertFalse(contains_title("Test 123", "Other words"))

    def test_parse(self):
        self.assertEqual(parse_for_url("Test 1-2-3"), "test-1-2-3")
        self.assertEqual(parse_for_url("Test & 1-2-3"), "test-1-2-3")