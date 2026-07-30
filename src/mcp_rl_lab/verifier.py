"""Deterministic public, held-out, and performance verification."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from mcp_rl_lab.config import Settings
from mcp_rl_lab.models import Classification, ProcessEvidence, VerificationResult
from mcp_rl_lab.patch_applier import apply_patch
from mcp_rl_lab.process import run_command
from mcp_rl_lab.task_loader import TaskPackage
from mcp_rl_lab.workspace_manager import CandidateWorkspace

COMPILERS = {"javac", "rustc", "clang++"}


def _run_commands(
    commands: list[list[str]], workspace: Path, settings: Settings, timeout: int
) -> list[ProcessEvidence]:
    results: list[ProcessEvidence] = []
    for command in commands:
        evidence = run_command(
            command,
            workspace,
            timeout_seconds=min(timeout, settings.command_timeout_seconds),
            max_output_bytes=settings.max_output_bytes,
        )
        results.append(evidence)
        if evidence.exit_code != 0 or evidence.timed_out:
            break
    return results


def _failure_classification(results: list[ProcessEvidence], hidden: bool = False) -> Classification:
    failed = next(result for result in results if result.exit_code != 0 or result.timed_out)
    if failed.timed_out:
        return "runtime_error"
    if Path(failed.command[0]).name in COMPILERS:
        return "compile_error"
    return "hidden_test_failure" if hidden else "test_failure"


def _changed_files(workspace: Path) -> list[str]:
    output = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=workspace,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return sorted(line for line in output.splitlines() if line)


def verify_patch(
    task: TaskPackage, patch: Path, settings: Settings | None = None
) -> VerificationResult:
    settings = settings or Settings.from_env()
    effective_settings = Settings(
        max_tool_calls=min(settings.max_tool_calls, task.manifest.resource_limits.max_tool_calls),
        command_timeout_seconds=min(
            settings.command_timeout_seconds,
            task.manifest.resource_limits.command_timeout_seconds,
        ),
        max_output_bytes=min(
            settings.max_output_bytes, task.manifest.resource_limits.max_output_bytes
        ),
        network_enabled=settings.network_enabled and task.manifest.resource_limits.network_enabled,
    )
    started = time.monotonic()
    public: list[ProcessEvidence] = []
    held_out: list[ProcessEvidence] = []
    benchmarks: list[ProcessEvidence] = []
    errors: list[str] = []
    classification: Classification = "incomplete_task"
    changed: list[str] = []
    exclusions_verified = False

    with CandidateWorkspace(task) as workspace:
        exclusions_verified = workspace.excluded_assets_absent()
        try:
            apply_patch(workspace.path, patch, task.manifest.allowed_changes)
        except PermissionError as error:
            classification = "contract_violation"
            errors.append(str(error))
        except (ValueError, subprocess.SubprocessError, UnicodeError) as error:
            classification = "malformed_patch"
            errors.append(str(error))
        else:
            changed = _changed_files(workspace.path)
            public = _run_commands(
                task.manifest.commands.public,
                workspace.path,
                effective_settings,
                task.manifest.timeout_seconds,
            )
            if any(result.exit_code != 0 or result.timed_out for result in public):
                classification = _failure_classification(public)
            else:
                workspace.overlay_held_out_tests()
                held_out = _run_commands(
                    task.manifest.commands.held_out,
                    workspace.path,
                    effective_settings,
                    task.manifest.timeout_seconds,
                )
                if any(result.exit_code != 0 or result.timed_out for result in held_out):
                    classification = _failure_classification(held_out, hidden=True)
                else:
                    benchmarks = _run_commands(
                        task.manifest.commands.benchmark,
                        workspace.path,
                        effective_settings,
                        task.manifest.timeout_seconds,
                    )
                    if any(result.exit_code != 0 or result.timed_out for result in benchmarks):
                        classification = "performance_regression"
                    else:
                        classification = "accepted"

    return VerificationResult(
        classification=classification,
        accepted=classification == "accepted",
        changed_files=changed,
        public_results=public,
        held_out_results=held_out,
        benchmark_results=benchmarks,
        errors=errors,
        candidate_workspace_exclusions_verified=exclusions_verified,
        duration_ms=int((time.monotonic() - started) * 1000),
    )
