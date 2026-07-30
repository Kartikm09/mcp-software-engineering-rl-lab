"""Ordered trace collection for local MCP calls."""

from __future__ import annotations

import time

from mcp_rl_lab.models import ToolCall, ToolResult, ToolTraceEntry


class TraceRecorder:
    def __init__(self) -> None:
        self.entries: list[ToolTraceEntry] = []

    def record(self, call: ToolCall, invoke) -> ToolResult:
        started = time.monotonic()
        result = invoke()
        self.entries.append(
            ToolTraceEntry(
                sequence=len(self.entries) + 1,
                call=call,
                result=result,
                duration_ms=int((time.monotonic() - started) * 1000),
            )
        )
        return result
