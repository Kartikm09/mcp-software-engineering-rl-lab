"""Resettable allowlisted candidate copies; trusted synthetic inputs only."""

import hashlib
import shutil
import tempfile
from pathlib import Path, PurePosixPath

from .catalog import task_root


class Workspace:
    def __init__(self, task_id):
        self.temp = tempfile.TemporaryDirectory(prefix="synthetic-candidate-")
        self.path = Path(self.temp.name) / "candidate"
        shutil.copytree(task_root(task_id) / "candidate", self.path)
        self.initial = self.snapshot()

    def snapshot(self):
        result = {}
        for path in self.path.rglob("*"):
            if path.is_symlink():
                raise ValueError("candidate symlinks are forbidden")
            if path.is_file():
                result[path.relative_to(self.path).as_posix()] = hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
        return result

    def apply(self, changes):
        if not isinstance(changes, dict) or set(changes) != {"solution.py"}:
            raise ValueError("only solution.py is writable")
        # Check the whole tree before writes and ensure no parent/file is a symlink.
        self.snapshot()
        for name, text in changes.items():
            path = PurePosixPath(name)
            target = self.path / name
            if (
                path.is_absolute()
                or ".." in path.parts
                or target.is_symlink()
                or target.resolve().parent != self.path.resolve()
                or not isinstance(text, str)
                or len(text.encode()) > 50000
            ):
                raise ValueError("invalid candidate path/content")
            target.write_text(text)
        return self.changed_files()

    def changed_files(self):
        current = self.snapshot()
        changed = sorted(
            k for k in set(current) | set(self.initial) if current.get(k) != self.initial.get(k)
        )
        if set(changed) - {"solution.py"}:
            raise ValueError("unauthorized candidate changes")
        return [
            {"path": k, "before_sha256": self.initial.get(k), "after_sha256": current.get(k)}
            for k in changed
        ]

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.temp.cleanup()
