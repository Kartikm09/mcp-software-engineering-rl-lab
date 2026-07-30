"""Load and validate self-contained engineering task packages."""

from __future__ import annotations

from pathlib import Path

import yaml

from mcp_rl_lab.models import TaskManifest


class TaskPackage:
    def __init__(self, root: Path, manifest: TaskManifest) -> None:
        self.root = root.resolve()
        self.manifest = manifest

    def path(self, relative: str) -> Path:
        candidate = (self.root / relative).resolve()
        if not candidate.is_relative_to(self.root):
            raise ValueError(f"task path escapes package root: {relative}")
        return candidate


def load_task(root: Path) -> TaskPackage:
    manifest_path = root / "task.yaml"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"missing task manifest: {manifest_path}")
    payload = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    package = TaskPackage(root, TaskManifest.model_validate(payload))
    required = [
        package.path(package.manifest.baseline_path),
        package.path(package.manifest.public_tests_path),
        package.path(package.manifest.held_out_tests_path),
        package.path(package.manifest.golden_patch_path),
        package.path(package.manifest.expected_trace_path),
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"incomplete task package: {', '.join(missing)}")
    return package


def discover_tasks(root: Path) -> list[TaskPackage]:
    return [load_task(path.parent) for path in sorted(root.rglob("task.yaml"))]
