"""Create candidate-visible and internal evaluator workspaces."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from mcp_rl_lab.task_loader import TaskPackage


class CandidateWorkspace:
    def __init__(self, task: TaskPackage) -> None:
        self.task = task
        self._temporary = tempfile.TemporaryDirectory(prefix=f"mcp-rl-{task.manifest.id}-")
        self.path = Path(self._temporary.name) / "candidate"
        self.path.mkdir(parents=True)
        shutil.copytree(task.path(task.manifest.baseline_path), self.path, dirs_exist_ok=True)
        shutil.copytree(task.path(task.manifest.public_tests_path), self.path, dirs_exist_ok=True)
        (self.path / "build").mkdir(exist_ok=True)
        self._initialize_git()

    def _initialize_git(self) -> None:
        import subprocess

        subprocess.run(["git", "init", "-q"], cwd=self.path, check=True)
        subprocess.run(
            ["git", "config", "user.email", "evaluator@example.invalid"],
            cwd=self.path,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "MCP RL Evaluator"],
            cwd=self.path,
            check=True,
        )
        subprocess.run(["git", "add", "."], cwd=self.path, check=True)
        subprocess.run(["git", "commit", "-qm", "candidate baseline"], cwd=self.path, check=True)

    def overlay_held_out_tests(self) -> None:
        shutil.copytree(
            self.task.path(self.task.manifest.held_out_tests_path),
            self.path,
            dirs_exist_ok=True,
        )

    def excluded_assets_absent(self) -> bool:
        forbidden = {"held_out_tests", "golden", "incorrect_patches"}
        return not any((self.path / name).exists() for name in forbidden)

    def close(self) -> None:
        self._temporary.cleanup()

    def __enter__(self) -> CandidateWorkspace:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()
