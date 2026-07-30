from __future__ import annotations

import json

from jsonschema import Draft202012Validator

from mcp_rl_lab.environment import run_episode
from tests.conftest import ROOT


def test_golden_episode_reward_is_transparent_and_repeatable(python_task, monkeypatch) -> None:
    monkeypatch.setenv("MCP_RL_FIXED_TIMESTAMP", "2026-07-30T00:00:00Z")
    patch = python_task.path(python_task.manifest.golden_patch_path)
    explanation = python_task.path("golden/explanation.md").read_text()
    first = run_episode(python_task, patch, final_explanation=explanation)
    second = run_episode(python_task, patch, final_explanation=explanation)
    assert first.episode_id == second.episode_id
    assert first.reward == second.reward
    assert first.reward.patch_correctness == 1
    assert first.reward.held_out_tests == 1
    assert first.reward.total >= 95
    schema = json.loads((ROOT / "schemas/reward.schema.json").read_text())
    Draft202012Validator(schema).validate(first.reward.model_dump(mode="json"))
