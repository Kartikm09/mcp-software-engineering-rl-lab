class Scheduler:
    def __init__(self):
        self.jobs = {}

    def schedule(self, identifier, due, payload):
        if identifier in self.jobs:
            job = self.jobs[identifier]
            if (job["original_due"], job["payload"]) != (due, payload):
                raise ValueError("conflicting schedule")
            return
        self.jobs[identifier] = {
            "due": due,
            "original_due": due,
            "payload": payload,
            "status": "pending",
            "attempts": 0,
        }

    def cancel(self, identifier):
        job = self.jobs[identifier]
        if job["status"] in {"pending", "retry"}:
            job["status"] = "cancelled"
            return True
        return False

    def run(self, now, effect):
        for identifier, job in self.jobs.items():
            if job["status"] not in {"pending", "retry"} or job["due"] > now:
                continue
            job["attempts"] += 1
            try:
                effect(identifier, job["payload"])
            except Exception:
                job["status"] = "retry" if job["attempts"] < 3 else "failed"
                job["due"] = now + 2
            else:
                job["status"] = "done"
