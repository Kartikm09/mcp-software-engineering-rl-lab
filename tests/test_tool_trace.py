from __future__ import annotations

import json

from jsonschema import Draft202012Validator

from mcp_rl_lab.models import ToolCall, ToolResult
from mcp_rl_lab.task_loader import discover_tasks
from mcp_rl_lab.trace_recorder import TraceRecorder
from tests.conftest import ROOT


def test_trace_recorder_preserves_sequence_and_structured_result() -> None:
    recorder = TraceRecorder()
    call = ToolCall(server="repository", tool="list_files", arguments={})
    result = recorder.record(call, lambda: ToolResult(ok=True, content={"files": []}))
    assert result.ok
    assert recorder.entries[0].sequence == 1
    assert recorder.entries[0].call == call


def test_expected_traces_are_valid_and_cover_required_tools() -> None:
    schema = json.loads((ROOT / "schemas/tool_trace.schema.json").read_text())
    validator = Draft202012Validator(schema)
    for task in discover_tasks(ROOT / "tasks"):
        payload = json.loads(task.path(task.manifest.expected_trace_path).read_text())
        validator.validate(payload)
        called = {f"{item['server']}.{item['tool']}" for item in payload["calls"]}
        assert set(task.manifest.required_tools) <= called
