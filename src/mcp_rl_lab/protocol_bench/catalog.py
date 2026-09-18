"""Evaluator-side versioned synthetic corpus, never copied into candidate roots."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3] / "protocol_tasks"
TASKS = ("duplicate-work", "scheduled-delivery", "module-boundary", "repeated-validation")


def task_root(task_id: str) -> Path:
    if task_id not in TASKS:
        raise ValueError("unknown task")
    return ROOT / task_id


def load(task_id: str) -> dict:
    return json.loads((task_root(task_id) / "manifest.json").read_text())
