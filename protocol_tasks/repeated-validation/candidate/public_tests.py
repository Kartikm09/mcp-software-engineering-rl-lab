import unittest

from solution import compute


class PublicContract(unittest.TestCase):
    def test_one_record(self):
        self.assertEqual(compute([{"sku": "a", "qty": 2}]), [("a", 14)])


if __name__ == "__main__":
    unittest.main()
