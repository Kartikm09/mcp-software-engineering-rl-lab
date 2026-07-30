"""Machine-readable and reviewer-ready episode reports."""

from __future__ import annotations

from pathlib import Path

from mcp_rl_lab.models import Episode


def write_episode(episode: Episode, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "episode.json").write_text(
        episode.model_dump_json(indent=2) + "\n", encoding="utf-8"
    )
    (output_dir / "episode-report.md").write_text(
        render_episode_markdown(episode), encoding="utf-8"
    )


def render_episode_markdown(episode: Episode) -> str:
    lines = [
        "# Coding-Agent Episode Report",
        "",
        "> Synthetic local task and evidence. This is not a private benchmark result.",
        "",
        f"- Episode: `{episode.episode_id}`",
        f"- Task: `{episode.task_id}`",
        f"- Classification: **{episode.verification.classification}**",
        f"- Reward: **{episode.reward.total:.2f}/100**",
        "- Candidate exclusions verified: "
        f"**{episode.verification.candidate_workspace_exclusions_verified}**",
        "",
        "## Tool Trace",
        "",
        "| # | Server | Tool | Result |",
        "| ---: | --- | --- | --- |",
    ]
    for entry in episode.tool_trace:
        lines.append(
            f"| {entry.sequence} | `{entry.call.server}` | `{entry.call.tool}` | "
            f"{'ok' if entry.result.ok else entry.result.error_code} |"
        )
    lines.extend(["", "## Changed Files", ""])
    lines.extend(f"- `{path}`" for path in episode.verification.changed_files)
    lines.extend(["", "## Verification Evidence", ""])
    for label, evidence in (
        ("Public", episode.verification.public_results),
        ("Held-out", episode.verification.held_out_results),
        ("Benchmark", episode.verification.benchmark_results),
    ):
        if not evidence:
            continue
        lines.append(f"### {label}")
        for item in evidence:
            lines.append(
                f"- `{' '.join(item.command)}`: exit={item.exit_code}, "
                f"duration={item.duration_ms}ms"
            )
    lines.extend(
        [
            "",
            "## Final Explanation",
            "",
            episode.final_explanation,
            "",
            "## Security Boundary",
            "",
            "The evaluator uses path validation, an executable allowlist, filtered environment "
            "variables, timeouts, and output caps. It is not a hardened production sandbox.",
        ]
    )
    return "\n".join(lines) + "\n"
