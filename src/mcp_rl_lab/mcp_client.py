"""In-process MCP-compatible client used for deterministic episodes."""

from __future__ import annotations

from mcp_rl_lab.models import ToolCall, ToolResult
from mcp_rl_lab.trace_recorder import TraceRecorder
from mcp_servers.toolkit import LocalToolRegistry


class LocalMCPClient:
    def __init__(self, registry: LocalToolRegistry, recorder: TraceRecorder) -> None:
        self.registry = registry
        self.recorder = recorder

    def call(self, server: str, tool: str, arguments: dict[str, object]) -> ToolResult:
        call = ToolCall(server=server, tool=tool, arguments=arguments)
        return self.recorder.record(call, lambda: self.registry.call(server, tool, arguments))
