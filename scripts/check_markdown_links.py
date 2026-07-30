"""Check relative Markdown links and image references without network access."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
EXCLUDED = {".git", ".venv", ".pytest_cache", ".ruff_cache"}


def main() -> int:
    failures: list[str] = []
    checked = 0
    for markdown in sorted(ROOT.rglob("*.md")):
        if any(part in EXCLUDED for part in markdown.parts):
            continue
        for target in LINK.findall(markdown.read_text(encoding="utf-8")):
            target = target.strip().split(maxsplit=1)[0].strip("<>")
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            relative = unquote(target.split("#", maxsplit=1)[0])
            if not relative:
                continue
            checked += 1
            resolved = (markdown.parent / relative).resolve()
            if not resolved.is_relative_to(ROOT) or not resolved.exists():
                failures.append(f"{markdown.relative_to(ROOT)} -> {target}")
    if failures:
        print("\n".join(failures))
        return 1
    print(f"Markdown link check: {checked} local references resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
