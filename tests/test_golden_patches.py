from __future__ import annotations

import pytest

from mcp_rl_lab.task_loader import discover_tasks
from mcp_rl_lab.verifier import verify_patch
from tests.conftest import ROOT


@pytest.mark.toolchains
def test_every_golden_patch_passes_and_every_negative_control_fails() -> None:
    for task in discover_tasks(ROOT / "tasks"):
        golden = verify_patch(task, task.path(task.manifest.golden_patch_path))
        assert golden.accepted, f"{task.manifest.id}: {golden.model_dump()}"
        for incorrect in task.manifest.incorrect_patch_paths:
            result = verify_patch(task, task.path(incorrect))
            assert not result.accepted, f"negative control accepted for {task.manifest.id}"
