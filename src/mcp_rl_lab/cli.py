"""CLI for task discovery, verification, and episode reports."""

from __future__ import annotations

from pathlib import Path

import typer

from mcp_rl_lab.environment import run_episode
from mcp_rl_lab.report import write_episode
from mcp_rl_lab.task_loader import discover_tasks, load_task
from mcp_rl_lab.verifier import verify_patch

app = typer.Typer(no_args_is_help=True, help="Run local MCP coding-agent evaluation tasks.")


@app.command("catalogue")
def catalogue(tasks_root: Path = Path("tasks")) -> None:
    for task in discover_tasks(tasks_root):
        typer.echo(
            f"{task.manifest.id}\t{task.manifest.language}\t{task.manifest.task_type}\t"
            f"{task.manifest.title}"
        )


@app.command("verify")
def verify_command(task_path: Path, patch: Path, output: Path | None = None) -> None:
    result = verify_patch(load_task(task_path), patch)
    typer.echo(f"classification={result.classification} accepted={result.accepted}")
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")
    if not result.accepted:
        raise typer.Exit(1)


@app.command("episode")
def episode_command(
    task_path: Path,
    patch: Path,
    output_dir: Path = Path("reports/generated/episode"),
    trace: Path | None = None,
    explanation: str = (
        "The patch addresses the discovered contract and preserves behavior under public "
        "and held-out verification."
    ),
) -> None:
    episode = run_episode(
        load_task(task_path),
        patch,
        trace_path=trace,
        final_explanation=explanation,
    )
    write_episode(episode, output_dir)
    typer.echo(
        f"{episode.episode_id}: classification={episode.verification.classification} "
        f"reward={episode.reward.total:.2f}"
    )
    if not episode.verification.accepted:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
