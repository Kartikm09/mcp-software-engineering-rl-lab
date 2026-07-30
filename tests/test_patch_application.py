from __future__ import annotations

import pytest

from mcp_rl_lab.patch_applier import apply_patch, patch_paths
from mcp_rl_lab.workspace_manager import CandidateWorkspace


def test_golden_patch_applies_only_to_allowed_file(python_task) -> None:
    patch = python_task.path(python_task.manifest.golden_patch_path)
    assert patch_paths(patch.read_text()) == ["retry.py"]
    with CandidateWorkspace(python_task) as workspace:
        changed = apply_patch(workspace.path, patch, python_task.manifest.allowed_changes)
        assert changed == ["retry.py"]
        assert "attempt - 1" in (workspace.path / "retry.py").read_text()


def test_prohibited_file_change_is_rejected(python_task, tmp_path) -> None:
    patch = tmp_path / "prohibited.patch"
    patch.write_text(
        "diff --git a/new.txt b/new.txt\n--- /dev/null\n+++ b/new.txt\n@@ -0,0 +1 @@\n+no\n"
    )
    with (
        CandidateWorkspace(python_task) as workspace,
        pytest.raises(PermissionError, match="prohibited file change"),
    ):
        apply_patch(workspace.path, patch, python_task.manifest.allowed_changes)


def test_traversal_path_is_rejected() -> None:
    with pytest.raises(ValueError, match="unsafe relative path"):
        patch_paths("--- a/../outside\n+++ b/../outside\n")
