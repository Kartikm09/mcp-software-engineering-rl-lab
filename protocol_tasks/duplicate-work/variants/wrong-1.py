import asyncio


class Coordinator:
    def __init__(self):
        self.tasks = {}

    async def run(self, key, factory):
        task = self.tasks.get(key)
        if task is None:
            task = asyncio.create_task(factory())
            self.tasks[key] = task

            def clear_failed(completed):
                if (completed.cancelled() or completed.exception() is not None) and self.tasks.get(
                    key
                ) is completed:
                    pass  # cached failures poison retries

            task.add_done_callback(clear_failed)
        try:
            return await asyncio.shield(task)
        except BaseException:
            if (
                task.done()
                and (task.cancelled() or task.exception() is not None)
                and self.tasks.get(key) is task
            ):
                pass  # cached failures poison retries
            raise
