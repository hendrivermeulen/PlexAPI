from unittest import TestCase

from utils.utils import contains_title, parse_for_url, await_value, remove_non_alpha, contains_at_least_half

count = 0


def get_count():
    global count
    count += 1
    if count == 3:
        return True
    return False


class Test(TestCase):
    def test_remove_non_alpha(self):
        self.assertEqual("test", remove_non_alpha("*/test%"))
        self.assertEqual("test", remove_non_alpha("test"))
        self.assertEqual("t1est1", remove_non_alpha(" t1est1"))
        self.assertEqual("test123", remove_non_alpha("test123"))

    def test_contains_at_least_half(self):
        self.assertTrue(contains_at_least_half("Ironman 2022", "Ironman 2022"))
        self.assertTrue(contains_at_least_half("Ironman 2022", "Ironman"))
        self.assertTrue(contains_at_least_half("Ironman 2022", "The Ironman"))

    def test_contains_title(self):
        self.assertTrue(contains_title("Test 123", "Test 123"))
        self.assertTrue(contains_title("Test 123", "Extra Test 123 Extra"))
        self.assertTrue(contains_title("Test 123", "Extra.Test.123.Extra"))
        self.assertTrue(contains_title("Test-123", "Extra.Test-123.Extra"))

        self.assertTrue(contains_title("Mission: Impossible - Dead Reckoning Part One 1080p",
                                       "Mission Impossible - Dead Reckoning Part One (2023) [1080p] [WEBRip]"))

        self.assertFalse(contains_title("Test 123", ""))
        self.assertFalse(contains_title("Test 123", "Other words"))

    def test_parse_for_url(self):
        self.assertEqual(parse_for_url("Test 1-2-3"), "test-1-2-3")
        self.assertEqual(parse_for_url("Test & 1-2-3"), "test-1-2-3")

    def test_await_true(self):
        self.assertTrue(await_value(lambda: True, True, 1000))
        self.assertFalse(await_value(lambda: False, True, 200))
        self.assertTrue(await_value(get_count, True, 1000))
