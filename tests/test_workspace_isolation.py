from __future__ import annotations

from mcp_rl_lab.workspace_manager import CandidateWorkspace


def test_candidate_workspace_excludes_evaluator_only_assets(python_task) -> None:
    with CandidateWorkspace(python_task) as workspace:
        assert workspace.excluded_assets_absent()
        assert (workspace.path / "retry.py").is_file()
        assert (workspace.path / "test_public.py").is_file()
        assert not (workspace.path / "test_held_out.py").exists()
        candidate_text = "\n".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in workspace.path.rglob("*")
            if path.is_file() and ".git" not in path.parts
        )
        assert "2 ** (attempt - 1)" not in candidate_text


def test_held_out_tests_are_overlaid_only_for_internal_verification(python_task) -> None:
    with CandidateWorkspace(python_task) as workspace:
        workspace.overlay_held_out_tests()
        assert (workspace.path / "test_held_out.py").is_file()
