"""Configuration, deterministic time, and toolchain resolution."""

from __future__ import annotations

import os
import shutil
import sys
from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class Settings:
    max_tool_calls: int = 40
    command_timeout_seconds: int = 30
    max_output_bytes: int = 200_000
    network_enabled: bool = False

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            max_tool_calls=int(os.getenv("MCP_RL_MAX_TOOL_CALLS", "40")),
            command_timeout_seconds=int(os.getenv("MCP_RL_COMMAND_TIMEOUT_SECONDS", "30")),
            max_output_bytes=int(os.getenv("MCP_RL_MAX_OUTPUT_BYTES", "200000")),
            network_enabled=os.getenv("MCP_RL_NETWORK_ENABLED", "0") == "1",
        )


def timestamp() -> datetime:
    fixed = os.getenv("MCP_RL_FIXED_TIMESTAMP")
    if fixed:
        return datetime.fromisoformat(fixed.replace("Z", "+00:00")).astimezone(UTC)
    return datetime.now(UTC)


TOOLCHAIN_ENV = {
    "$PYTHON": None,
    "$JAVA": "MCP_RL_JAVA",
    "$JAVAC": "MCP_RL_JAVAC",
    "$RUSTC": "MCP_RL_RUSTC",
    "$GO": "MCP_RL_GO",
    "$NODE": "MCP_RL_NODE",
    "$CLANGXX": "MCP_RL_CLANGXX",
}

TOOLCHAIN_DEFAULT = {
    "$JAVA": "java",
    "$JAVAC": "javac",
    "$RUSTC": "rustc",
    "$GO": "go",
    "$NODE": "node",
    "$CLANGXX": "clang++",
}


def resolve_executable(token: str) -> str:
    if token == "$PYTHON":
        return sys.executable
    if token not in TOOLCHAIN_ENV:
        return token
    env_name = TOOLCHAIN_ENV[token]
    configured = os.getenv(env_name, "") if env_name else ""
    executable = configured or TOOLCHAIN_DEFAULT[token]
    resolved = shutil.which(executable) if not os.path.isabs(executable) else executable
    if not resolved:
        raise FileNotFoundError(f"required toolchain executable is unavailable: {executable}")
    return resolved


def resolve_command(command: list[str]) -> list[str]:
    if not command:
        raise ValueError("empty commands are not allowed")
    return [resolve_executable(command[0]), *command[1:]]
