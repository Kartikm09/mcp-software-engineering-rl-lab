from __future__ import annotations

from pathlib import Path

import pytest

from mcp_rl_lab.task_loader import TaskPackage, load_task

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def python_task() -> TaskPackage:
    return load_task(ROOT / "tasks/bug_fixing/python-retry-backoff")
