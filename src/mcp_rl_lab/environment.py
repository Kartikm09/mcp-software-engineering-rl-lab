"""Episode orchestration across MCP discovery, patch verification, and reward."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from mcp_rl_lab.config import Settings, timestamp
from mcp_rl_lab.mcp_client import LocalMCPClient
from mcp_rl_lab.models import Episode
from mcp_rl_lab.reward import calculate_reward
from mcp_rl_lab.task_loader import TaskPackage
from mcp_rl_lab.trace_recorder import TraceRecorder
from mcp_rl_lab.verifier import verify_patch
from mcp_servers.toolkit import LocalToolRegistry


def run_episode(
    task: TaskPackage,
    patch: Path,
    *,
    trace_path: Path | None = None,
    final_explanation: str,
    settings: Settings | None = None,
) -> Episode:
    settings = settings or Settings.from_env()
    start = timestamp()
    recorder = TraceRecorder()
    registry = LocalToolRegistry(task, settings)
    client = LocalMCPClient(registry, recorder)
    trace_payload = json.loads(
        (trace_path or task.path(task.manifest.expected_trace_path)).read_text(encoding="utf-8")
    )
    calls = trace_payload["calls"]
    tool_call_limit = min(settings.max_tool_calls, task.manifest.resource_limits.max_tool_calls)
    if len(calls) > tool_call_limit:
        raise ValueError("tool-call limit exceeded")
    for item in calls:
        client.call(item["server"], item["tool"], item.get("arguments", {}))

    verification = verify_patch(task, patch, settings)
    used = {f"{entry.call.server}.{entry.call.tool}" for entry in recorder.entries}
    missing_tools = sorted(set(task.manifest.required_tools) - used)
    failed_evidence = [entry for entry in recorder.entries if not entry.result.ok]
    if verification.accepted and missing_tools:
        verification = verification.model_copy(
            update={
                "accepted": False,
                "classification": "incorrect_tool_use",
                "errors": [f"missing required tool evidence: {', '.join(missing_tools)}"],
            }
        )
    elif verification.accepted and failed_evidence:
        verification = verification.model_copy(
            update={
                "accepted": False,
                "classification": "missing_evidence",
                "errors": ["one or more required evidence calls failed"],
            }
        )

    reward = calculate_reward(task.manifest, recorder.entries, verification, final_explanation)
    patch_digest = hashlib.sha256(patch.read_bytes()).hexdigest()
    episode_identity = f"{task.manifest.id}|{patch_digest}|{len(recorder.entries)}"
    return Episode(
        episode_id=f"episode-{hashlib.sha256(episode_identity.encode()).hexdigest()[:12]}",
        task_id=task.manifest.id,
        initial_prompt=task.manifest.initial_prompt,
        available_servers=registry.servers,
        tool_trace=recorder.entries,
        patch_sha256=patch_digest,
        final_explanation=final_explanation,
        verification=verification,
        reward=reward,
        started_at=start,
        completed_at=timestamp(),
    )
