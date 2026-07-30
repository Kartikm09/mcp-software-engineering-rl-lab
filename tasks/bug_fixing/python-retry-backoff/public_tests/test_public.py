import unittest

from retry import backoff_delay


class RetryBackoffPublicTests(unittest.TestCase):
    def test_first_attempt_uses_base_delay(self) -> None:
        self.assertEqual(backoff_delay(1, base=2, cap=20), 2)

    def test_second_attempt_doubles(self) -> None:
        self.assertEqual(backoff_delay(2, base=2, cap=20), 4)


if __name__ == "__main__":
    unittest.main()
