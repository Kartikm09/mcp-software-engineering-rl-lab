"""Shared lazy registry for standalone MCP server processes."""

from __future__ import annotations

import os
from pathlib import Path

from mcp_rl_lab.task_loader import load_task
from mcp_servers.toolkit import LocalToolRegistry


def registry() -> LocalToolRegistry:
    task_root = os.getenv("MCP_RL_TASK_ROOT")
    if not task_root:
        raise RuntimeError("MCP_RL_TASK_ROOT must identify one local task package")
    return LocalToolRegistry(load_task(Path(task_root)))


def content(server: str, tool: str, arguments: dict[str, object]) -> dict[str, object]:
    result = registry().call(server, tool, arguments)
    return result.model_dump(mode="json")
