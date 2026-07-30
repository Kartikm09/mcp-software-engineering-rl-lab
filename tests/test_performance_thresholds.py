from __future__ import annotations

import pytest

from mcp_rl_lab.task_loader import load_task
from mcp_rl_lab.verifier import verify_patch
from tests.conftest import ROOT


@pytest.mark.toolchains
def test_go_performance_task_has_deterministic_gate_and_real_benchmark() -> None:
    task = load_task(ROOT / "tasks/performance_optimisation/go-dedupe-index")
    result = verify_patch(task, task.path(task.manifest.golden_patch_path))
    assert result.accepted
    assert task.manifest.performance_threshold
    assert len(result.benchmark_results) == 1
    assert "BenchmarkUnique" in result.benchmark_results[0].stdout


def test_performance_weight_is_not_style_dominated() -> None:
    task = load_task(ROOT / "tasks/performance_optimisation/go-dedupe-index")
    weights = task.manifest.reward_weights
    assert weights.performance > weights.maintainability
    assert weights.patch_correctness + weights.public_tests + weights.held_out_tests >= 0.55
