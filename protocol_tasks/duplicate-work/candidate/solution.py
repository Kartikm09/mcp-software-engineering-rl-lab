class Coordinator:
    async def run(self, key, factory):
        return await factory()
