import unittest

from solution import normalize


class PublicContract(unittest.TestCase):
    def test_ascii_record(self):
        self.assertEqual(normalize(" A ", True), {"name": "a", "enabled": True})


if __name__ == "__main__":
    unittest.main()
