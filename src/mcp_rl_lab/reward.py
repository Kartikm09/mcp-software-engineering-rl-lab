"""Transparent reward calculation with correctness weighted above style."""

from __future__ import annotations

from mcp_rl_lab.models import RewardBreakdown, TaskManifest, ToolTraceEntry, VerificationResult


def calculate_reward(
    task: TaskManifest,
    trace: list[ToolTraceEntry],
    verification: VerificationResult,
    final_explanation: str,
) -> RewardBreakdown:
    used = {f"{entry.call.server}.{entry.call.tool}" for entry in trace}
    required = set(task.required_tools)
    successful = [entry for entry in trace if entry.result.ok]
    values = {
        "tool_discovery": min(1.0, len({entry.call.server for entry in trace}) / 3),
        "relevant_tool_selection": len(required & used) / len(required),
        "evidence_gathering": min(1.0, len(successful) / max(1, len(task.required_evidence))),
        "patch_correctness": 1.0 if verification.accepted else 0.0,
        "public_tests": 1.0
        if verification.public_results
        and all(item.exit_code == 0 for item in verification.public_results)
        else 0.0,
        "held_out_tests": 1.0
        if verification.held_out_results
        and all(item.exit_code == 0 for item in verification.held_out_results)
        else 0.0,
        "maintainability": 1.0
        if verification.changed_files
        and len(verification.changed_files) <= len(task.allowed_changes)
        else 0.0,
        "performance": 1.0
        if not task.commands.benchmark
        or all(item.exit_code == 0 for item in verification.benchmark_results)
        else 0.0,
        "final_explanation": 1.0 if len(final_explanation.split()) >= 12 else 0.0,
    }
    weights = task.reward_weights.model_dump()
    total = round(sum(values[key] * weights[key] for key in values) * 100, 2)
    return RewardBreakdown(**values, total=total)
