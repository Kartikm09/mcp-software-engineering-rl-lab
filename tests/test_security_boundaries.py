from __future__ import annotations

import os

import pytest

from mcp_rl_lab.safety import filtered_environment, safe_relative_path, validate_command


def test_path_traversal_and_network_commands_are_rejected() -> None:
    with pytest.raises(ValueError):
        safe_relative_path("../../private")
    with pytest.raises(ValueError, match="not allowlisted"):
        validate_command(["curl", "https://example.invalid"])
    with pytest.raises(ValueError, match="prohibited argument"):
        validate_command(["python", "https://example.invalid/script.py"])


def test_candidate_environment_filters_secrets(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PRIVATE_API_TOKEN", "synthetic-should-not-cross-boundary")
    environment = filtered_environment(tmp_path)
    assert "PRIVATE_API_TOKEN" not in environment
    assert environment["HOME"].startswith(str(tmp_path))
    assert environment["NO_PROXY"] == "*"
    assert os.path.isdir(environment["GOCACHE"])
