import asyncio


class Coordinator:
    def __init__(self):
        self.pending_or_done = {}

    async def run(self, key, factory):
        task = self.pending_or_done.get(key)
        if task is None:
            task = asyncio.create_task(factory())
            self.pending_or_done[key] = task

            def clear_failed(completed):
                if (
                    completed.cancelled() or completed.exception() is not None
                ) and self.pending_or_done.get(key) is completed:
                    self.pending_or_done.pop(key, None)

            task.add_done_callback(clear_failed)
        try:
            return await asyncio.shield(task)
        except BaseException:
            if (
                task.done()
                and (task.cancelled() or task.exception() is not None)
                and self.pending_or_done.get(key) is task
            ):
                self.pending_or_done.pop(key, None)
            raise
