import unittest

from solution import Scheduler


class PublicContract(unittest.TestCase):
    def test_due_call(self):
        scheduler = Scheduler()
        seen = []
        scheduler.schedule("one", 5, "parcel")
        scheduler.run(5, lambda key, payload: seen.append((key, payload)))
        self.assertEqual(seen, [("one", "parcel")])


if __name__ == "__main__":
    unittest.main()
