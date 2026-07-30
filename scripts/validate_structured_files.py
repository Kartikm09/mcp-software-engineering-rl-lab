"""Parse every committed JSON and YAML document with a strict failure summary."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {".git", ".venv", ".pytest_cache", ".ruff_cache", "reports/generated"}


def excluded(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    rendered = relative.as_posix()
    return any(part in EXCLUDED for part in relative.parts) or any(
        rendered.startswith(prefix) for prefix in EXCLUDED if "/" in prefix
    )


def main() -> int:
    parsed = 0
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or excluded(path):
            continue
        if path.suffix == ".json":
            json.loads(path.read_text(encoding="utf-8"))
            parsed += 1
        elif path.suffix in {".yaml", ".yml"}:
            yaml.safe_load(path.read_text(encoding="utf-8"))
            parsed += 1
    print(f"structured-file validation: {parsed} JSON/YAML files parsed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
