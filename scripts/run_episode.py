"""Generate one reproducible golden or candidate episode."""

from __future__ import annotations

import argparse
from pathlib import Path

from mcp_rl_lab.environment import run_episode
from mcp_rl_lab.report import write_episode
from mcp_rl_lab.task_loader import load_task


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task", type=Path)
    parser.add_argument("--patch", type=Path)
    parser.add_argument("--golden", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("reports/generated/episode"))
    args = parser.parse_args()
    task = load_task(args.task)
    patch = task.path(task.manifest.golden_patch_path) if args.golden else args.patch
    if patch is None:
        parser.error("provide --patch or --golden")
    explanation = task.path("golden/explanation.md").read_text(encoding="utf-8").strip()
    heading = "# Golden Explanation"
    if explanation.startswith(heading):
        explanation = explanation.removeprefix(heading).strip()
    episode = run_episode(task, patch, final_explanation=explanation)
    write_episode(episode, args.output)
    print(f"{episode.episode_id}: {episode.verification.classification} {episode.reward.total}")
    return 0 if episode.verification.accepted else 1


if __name__ == "__main__":
    raise SystemExit(main())
