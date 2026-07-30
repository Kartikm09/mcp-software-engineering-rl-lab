"""Validate task manifests, schemas, references, and negative controls."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from mcp_rl_lab.task_loader import discover_tasks

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    schema = json.loads((ROOT / "schemas/task.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    tasks = discover_tasks(ROOT / "tasks")
    if len(tasks) != 6:
        raise ValueError(f"expected six original tasks, found {len(tasks)}")
    for package in tasks:
        payload = yaml.safe_load((package.root / "task.yaml").read_text(encoding="utf-8"))
        validator.validate(payload)
        for path in package.manifest.incorrect_patch_paths:
            if not package.path(path).is_file():
                raise FileNotFoundError(f"missing incorrect patch: {path}")
        trace = json.loads(
            package.path(package.manifest.expected_trace_path).read_text(encoding="utf-8")
        )
        trace_schema = json.loads(
            (ROOT / "schemas/tool_trace.schema.json").read_text(encoding="utf-8")
        )
        Draft202012Validator(trace_schema).validate(trace)
        if not trace.get("calls"):
            raise ValueError(f"task {package.manifest.id} has no expected tool trace")
        called_tools = {f"{call['server']}.{call['tool']}" for call in trace["calls"]}
        missing_tools = sorted(set(package.manifest.required_tools) - called_tools)
        if missing_tools:
            raise ValueError(
                f"task {package.manifest.id} expected trace misses: {', '.join(missing_tools)}"
            )
    environment_schema = json.loads(
        (ROOT / "schemas/environment.schema.json").read_text(encoding="utf-8")
    )
    environment_validator = Draft202012Validator(environment_schema)
    environments = sorted((ROOT / "environments").glob("*/environment.yaml"))
    for descriptor in environments:
        environment_validator.validate(yaml.safe_load(descriptor.read_text(encoding="utf-8")))
    print(f"task package validation: {len(tasks)} tasks and {len(environments)} environments ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
