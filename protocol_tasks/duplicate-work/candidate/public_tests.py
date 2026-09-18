import asyncio
import unittest

from solution import Coordinator


class PublicContract(unittest.TestCase):
    def test_one_call(self):
        async def run():
            async def effect():
                return 42

            self.assertEqual(await Coordinator().run("one", effect), 42)

        asyncio.run(run())


if __name__ == "__main__":
    unittest.main()
