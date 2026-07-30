"""Resolve each recorded toolchain and emit a machine-readable environment report."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from mcp_rl_lab.config import resolve_executable

ROOT = Path(__file__).resolve().parents[1]
TOKENS = {
    "python": "$PYTHON",
    "java": "$JAVAC",
    "rust": "$RUSTC",
    "go": "$GO",
    "typescript": "$NODE",
    "cpp": "$CLANGXX",
}
VERSION_ARGUMENTS = {
    "$JAVAC": ["-version"],
    "$GO": ["version"],
    "$CLANGXX": ["--version"],
}


def main() -> int:
    schema = json.loads((ROOT / "schemas/environment.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    records: list[dict[str, object]] = []
    failures: list[str] = []
    for descriptor in sorted((ROOT / "environments").glob("*/environment.yaml")):
        payload = yaml.safe_load(descriptor.read_text(encoding="utf-8"))
        validator.validate(payload)
        token = TOKENS[payload["language"]]
        try:
            executable = resolve_executable(token)
            command = [executable, *VERSION_ARGUMENTS.get(token, ["--version"])]
            completed = subprocess.run(command, capture_output=True, text=True, check=False)
            version = (completed.stdout or completed.stderr).splitlines()[0]
            if completed.returncode:
                raise RuntimeError(version)
            status = "available"
        except (FileNotFoundError, RuntimeError, IndexError) as error:
            executable = None
            version = str(error)
            status = "unavailable"
            failures.append(payload["id"])
        task_path = ROOT / payload["task_path"]
        records.append(
            {
                "environment_id": payload["id"],
                "language": payload["language"],
                "task_path": payload["task_path"],
                "task_exists": task_path.is_dir(),
                "network": payload["network"],
                "status": status,
                "executable": Path(executable).name if executable else None,
                "version": version,
            }
        )
    output = ROOT / "reports/generated/toolchains.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"environments": records}, indent=2) + "\n", encoding="utf-8")
    print(f"environment build check: {len(records) - len(failures)}/{len(records)} available")
    return 1 if failures or any(not record["task_exists"] for record in records) else 0


if __name__ == "__main__":
    raise SystemExit(main())
