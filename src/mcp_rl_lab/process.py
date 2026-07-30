"""Bounded subprocess execution with structured evidence."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from mcp_rl_lab.config import resolve_command
from mcp_rl_lab.models import ProcessEvidence
from mcp_rl_lab.safety import filtered_environment, validate_command


def run_command(
    command: list[str],
    workspace: Path,
    *,
    timeout_seconds: int,
    max_output_bytes: int,
) -> ProcessEvidence:
    resolved = resolve_command(command)
    validate_command(resolved)
    start = time.monotonic()
    try:
        completed = subprocess.run(
            resolved,
            cwd=workspace,
            env=filtered_environment(workspace),
            capture_output=True,
            text=False,
            timeout=timeout_seconds,
            check=False,
        )
        stdout_bytes = completed.stdout
        stderr_bytes = completed.stderr
        truncated = len(stdout_bytes) + len(stderr_bytes) > max_output_bytes
        remaining = max_output_bytes
        stdout = stdout_bytes[:remaining]
        remaining -= len(stdout)
        stderr = stderr_bytes[: max(0, remaining)]
        return ProcessEvidence(
            command=command,
            exit_code=completed.returncode,
            duration_ms=int((time.monotonic() - start) * 1000),
            stdout=stdout.decode("utf-8", errors="replace"),
            stderr=stderr.decode("utf-8", errors="replace"),
            output_truncated=truncated,
        )
    except subprocess.TimeoutExpired as error:
        return ProcessEvidence(
            command=command,
            exit_code=None,
            duration_ms=int((time.monotonic() - start) * 1000),
            stdout=(error.stdout or b"")[:max_output_bytes].decode("utf-8", errors="replace"),
            stderr=(error.stderr or b"")[:max_output_bytes].decode("utf-8", errors="replace"),
            timed_out=True,
        )
