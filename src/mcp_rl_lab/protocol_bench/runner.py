"""No-key calibration runner using actual MCP servers and trusted synthetic variants."""

import argparse
import asyncio
import hashlib
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from .catalog import TASKS, load, task_root
from .client import Session, meaningful_usage
from .workspace import Workspace

VARIANTS = ("baseline", "reference", "alternative", "wrong-1", "wrong-2")


async def run_attempt(task_id, variant, output):
    if variant not in VARIANTS:
        raise ValueError("unknown synthetic variant")
    task = load(task_id)
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError("refusing to overwrite existing evidence")
    output.mkdir(parents=True, exist_ok=True)
    trace = []
    references = []
    handshakes = []
    # Fresh processes for every attempt/task; each server has its own immutable task scope.
    for kind, calls in [
        (
            "specification",
            [
                ("get_schema_version", {}),
                ("search_specs", {"query": " "}),
                ("get_requirement", {"record_id": "R-" + task_id, "version": "1"}),
            ],
        ),
        (
            "evidence",
            [
                (name, {"record_id": prefix + "-" + task_id, "version": "1"})
                for name, prefix in [
                    ("get_issue", "I"),
                    ("read_sanitized_log", "L"),
                    ("get_expected_transition", "T"),
                ]
            ],
        ),
    ]:
        async with Session(task_id, kind) as session:
            handshakes.append(
                {
                    "server": session.server_name,
                    "protocol_version": session.protocol_version,
                    "transport": "stdio",
                    "mode": "initialize/initialized",
                    "tools": session.tools,
                }
            )
            for name, arguments in calls:
                await session.call(name, arguments)
            for entry in session.trace:
                entry["sequence"] = len(trace) + 1
                trace.append(entry)
    with Workspace(task_id) as candidate:
        if variant != "baseline":
            content = (task_root(task_id) / "variants" / f"{variant}.py").read_text()
            candidate.apply({"solution.py": content})
        changed = candidate.changed_files()
        for entry in trace:
            response = entry.get("response", {})
            if response.get("source_id") in task["required_sources"]:
                references.append(
                    {
                        "source_id": response["source_id"],
                        "version": response["version"],
                        "response_sha256": entry["response_sha256"],
                        "path": "solution.py",
                        "decision": task["decision"],
                    }
                )
        verifier = Path(__file__).with_name("acceptance.py")
        env = {
            "PATH": str(Path(sys.executable).parent) + os.pathsep + os.defpath,
            "HOME": str(candidate.path),
            "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "TZ": "UTC",
        }
        command = [sys.executable, "-I", "-B", str(verifier), task_id, str(candidate.path)]
        try:
            process = subprocess.run(
                command, cwd=candidate.path, env=env, capture_output=True, text=True, timeout=10
            )
            functional = (
                json.loads(process.stdout)
                if process.returncode == 0
                else {
                    "passed": False,
                    "checks": [
                        {
                            "name": "verifier-launch",
                            "status": "infrastructure_error",
                            "exit_code": process.returncode,
                            "detail": process.stderr[-2000:],
                        }
                    ],
                }
            )
        except (subprocess.TimeoutExpired, json.JSONDecodeError) as error:
            functional = {
                "passed": False,
                "checks": [
                    {
                        "name": "verifier-response",
                        "status": "infrastructure_error",
                        "exit_code": 1,
                        "detail": type(error).__name__,
                    }
                ],
            }
        try:
            public = subprocess.run(
                [sys.executable, "-B", "public_tests.py"],
                cwd=candidate.path,
                env=env,
                capture_output=True,
                text=True,
                timeout=10,
            )
            public_result = {
                "name": "public-contract",
                "exit_code": public.returncode,
                "status": "passed" if public.returncode == 0 else "assertion_failed",
                "detail": public.stderr[-2000:],
            }
        except subprocess.TimeoutExpired:
            public_result = {
                "name": "public-contract",
                "exit_code": 1,
                "status": "infrastructure_error",
                "detail": "timeout",
            }
        functional["checks"].insert(0, public_result)
        functional["passed"] = functional["passed"] and public_result["exit_code"] == 0
        # Detect even non-source changes caused while executing the trusted candidate.
        changed = candidate.changed_files()
        usage = meaningful_usage(task_id, trace, references, [x["path"] for x in changed])
        result = {
            "task_id": task_id,
            "variant": variant,
            "functional": functional,
            "mcp_usage": usage,
            "accepted": functional["passed"] and usage["passed"],
            "classification": "synthetic-no-key-calibration",
        }
        manifest = {
            "task_id": task_id,
            "version": "1",
            "variant": variant,
            "created": datetime.now(UTC).isoformat(),
            "classification": result["classification"],
            "sdk": "mcp==2.0.0",
            "python": sys.version,
            "candidate_baseline_sha256": candidate.initial["solution.py"],
            "verifier_sha256": hashlib.sha256(verifier.read_bytes()).hexdigest(),
            "handshakes": handshakes,
            "trust": (
                "Trusted synthetic patches only. Public fixtures are inspectable; "
                "local subprocesses are not hostile-code containment."
            ),
        }
    for filename, value in [
        ("manifest.json", manifest),
        ("result.json", result),
        ("test_results.json", functional),
        ("changed_files.json", {"files": changed, "source_references": references}),
    ]:
        (output / filename).write_text(json.dumps(value, indent=2) + "\n")
    (output / "mcp_tool_trace.jsonl").write_text("".join(json.dumps(x) + "\n" for x in trace))
    (output / "reproduction.md").write_text(
        "# Reproduction\n\nSynthetic trusted calibration. In a clean development install run:\n\n"
        f"```sh\npython -m mcp_rl_lab.protocol_bench.runner {task_id} {variant} "
        "--output reports/generated/new-attempt\n```\n\n"
        "Use a new output directory. No model account, keys or external service required.\n"
    )
    (output / "review.md").write_text(
        "# Evidence review\n\nClassification: synthetic calibration.\n"
        "This is not a live coding-model attempt.\n\n"
        f"Functional acceptance: {functional['passed']}. "
        f"Meaningful MCP retrieval/reference linkage: {usage['passed']}.\n\n"
        "Independent behavior checks grade results, not patch similarity. "
        "Handshake/discovery metadata and visible tool calls are recorded. "
        "Reference decisions are scripted annotations, not hidden reasoning "
        "or a causal measure of understanding.\n"
    )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=TASKS)
    parser.add_argument("variant", choices=VARIANTS)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = asyncio.run(run_attempt(args.task, args.variant, args.output))
    print(json.dumps(result, indent=2))
    # Calibration CLI completes for expected negative controls; acceptance is explicit JSON.


if __name__ == "__main__":
    main()
