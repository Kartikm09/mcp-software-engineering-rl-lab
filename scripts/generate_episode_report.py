"""Render a saved canonical episode JSON document as Markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from mcp_rl_lab.models import Episode
from mcp_rl_lab.report import render_episode_markdown


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("episode", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    episode = Episode.model_validate(json.loads(args.episode.read_text(encoding="utf-8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_episode_markdown(episode), encoding="utf-8")
    print(f"episode report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
