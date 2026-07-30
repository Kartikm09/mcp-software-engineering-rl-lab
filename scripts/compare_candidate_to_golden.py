"""Compare deterministic candidate and golden verification evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from mcp_rl_lab.task_loader import load_task
from mcp_rl_lab.verifier import verify_patch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task", type=Path)
    parser.add_argument("candidate_patch", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    task = load_task(args.task)
    candidate = verify_patch(task, args.candidate_patch)
    golden = verify_patch(task, task.path(task.manifest.golden_patch_path))
    payload = {
        "task_id": task.manifest.id,
        "candidate": candidate.model_dump(mode="json"),
        "golden": golden.model_dump(mode="json"),
        "classification_match": candidate.classification == golden.classification,
        "changed_files_match": candidate.changed_files == golden.changed_files,
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if candidate.accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
