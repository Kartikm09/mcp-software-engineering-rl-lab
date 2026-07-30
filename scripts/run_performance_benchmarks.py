"""Run the golden patch for each benchmark task and retain reproducible evidence."""

from __future__ import annotations

import json
from pathlib import Path

from mcp_rl_lab.task_loader import discover_tasks
from mcp_rl_lab.verifier import verify_patch

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    records: list[dict[str, object]] = []
    failed = False
    for task in discover_tasks(ROOT / "tasks"):
        if not task.manifest.commands.benchmark:
            continue
        result = verify_patch(task, task.path(task.manifest.golden_patch_path))
        failed = failed or not result.accepted
        records.append(
            {
                "task_id": task.manifest.id,
                "classification": result.classification,
                "threshold": task.manifest.performance_threshold,
                "commands": [item.model_dump(mode="json") for item in result.benchmark_results],
            }
        )
    output = ROOT / "reports/generated/performance-benchmarks.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"benchmarks": records}, indent=2) + "\n", encoding="utf-8")
    print(f"performance benchmark verification: {len(records)} task(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
