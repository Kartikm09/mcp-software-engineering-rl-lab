"""Validate and apply candidate patches without permitting path escape."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from mcp_rl_lab.safety import is_allowed_change, safe_relative_path

DIFF_PATH = re.compile(r"^(?:---|\+\+\+) (?:[ab]/)?(.+)$")


def patch_paths(patch_text: str) -> list[str]:
    paths: list[str] = []
    for line in patch_text.splitlines():
        match = DIFF_PATH.match(line)
        if not match or match.group(1) == "/dev/null":
            continue
        path = match.group(1)
        safe_relative_path(path)
        if path not in paths:
            paths.append(path)
    if not paths:
        raise ValueError("patch does not declare any changed file")
    return paths


def apply_patch(workspace: Path, patch: Path, allowed_changes: list[str]) -> list[str]:
    if patch.stat().st_size > 1_000_000:
        raise ValueError("patch exceeds the 1 MB limit")
    patch_text = patch.read_text(encoding="utf-8")
    paths = patch_paths(patch_text)
    prohibited = [path for path in paths if not is_allowed_change(path, allowed_changes)]
    if prohibited:
        raise PermissionError(f"prohibited file change: {', '.join(prohibited)}")
    check = subprocess.run(
        ["git", "apply", "--check", "--whitespace=error-all", str(patch)],
        cwd=workspace,
        capture_output=True,
        text=True,
        check=False,
    )
    if check.returncode:
        raise ValueError(check.stderr.strip() or "patch failed validation")
    subprocess.run(["git", "apply", str(patch)], cwd=workspace, check=True)
    return paths
