import unittest

from retry import backoff_delay


class RetryBackoffHeldOutTests(unittest.TestCase):
    def test_later_attempt_remains_exponential(self) -> None:
        self.assertEqual(backoff_delay(4, base=1, cap=20), 8)

    def test_cap_is_preserved(self) -> None:
        self.assertEqual(backoff_delay(8, base=2, cap=16), 16)

    def test_invalid_attempt_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            backoff_delay(0)


if __name__ == "__main__":
    unittest.main()
