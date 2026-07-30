"""Verify every golden patch and confirm each negative control is rejected."""

from __future__ import annotations

from pathlib import Path

from mcp_rl_lab.task_loader import discover_tasks
from mcp_rl_lab.verifier import verify_patch

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    failures: list[str] = []
    for task in discover_tasks(ROOT / "tasks"):
        golden = verify_patch(task, task.path(task.manifest.golden_patch_path))
        print(f"{task.manifest.id}: golden={golden.classification}")
        if not golden.accepted:
            failures.append(f"{task.manifest.id}: golden {golden.classification}")
        for incorrect_path in task.manifest.incorrect_patch_paths:
            result = verify_patch(task, task.path(incorrect_path))
            print(f"{task.manifest.id}: negative={result.classification}")
            if result.accepted:
                failures.append(f"{task.manifest.id}: incorrect patch accepted")
    if failures:
        print("\n".join(failures))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
