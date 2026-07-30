"""Path, command, environment, and output safety helpers."""

from __future__ import annotations

import fnmatch
import os
from pathlib import Path, PurePosixPath

ALLOWED_EXECUTABLES = {
    "python",
    "python3",
    "java",
    "javac",
    "rustc",
    "go",
    "node",
    "clang++",
    "git",
    "rust-public",
    "rust-held",
    "cpp-public",
    "cpp-held",
}


def safe_relative_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError(f"unsafe relative path: {value}")
    return path


def is_allowed_change(path: str, patterns: list[str]) -> bool:
    safe_relative_path(path)
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def validate_command(command: list[str]) -> None:
    if not command:
        raise ValueError("empty command")
    executable = Path(command[0]).name
    if executable not in ALLOWED_EXECUTABLES:
        raise ValueError(f"executable is not allowlisted: {executable}")
    for argument in command[1:]:
        if "\x00" in argument or argument.startswith("http://") or argument.startswith("https://"):
            raise ValueError("command contains a prohibited argument")


def filtered_environment(workspace: Path) -> dict[str, str]:
    allowed = {"PATH", "LANG", "LC_ALL", "SYSTEMROOT", "TMPDIR"}
    environment = {key: value for key, value in os.environ.items() if key in allowed}
    environment.update(
        {
            "HOME": str(workspace / ".home"),
            "NO_PROXY": "*",
            "no_proxy": "*",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_TERMINAL_PROMPT": "0",
            "GOCACHE": str(workspace / ".cache" / "go-build"),
            "GOMODCACHE": str(workspace / ".cache" / "go-mod"),
        }
    )
    (workspace / ".home").mkdir(exist_ok=True)
    (workspace / ".cache" / "go-build").mkdir(parents=True, exist_ok=True)
    (workspace / ".cache" / "go-mod").mkdir(parents=True, exist_ok=True)
    return environment
