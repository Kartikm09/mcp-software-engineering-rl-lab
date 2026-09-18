import asyncio
import json
from pathlib import Path

import pytest

from mcp_rl_lab.protocol_bench.client import Session, meaningful_usage
from mcp_rl_lab.protocol_bench.runner import run_attempt
from mcp_rl_lab.protocol_bench.workspace import Workspace

TASKS = ["duplicate-work", "scheduled-delivery", "module-boundary", "repeated-validation"]


def test_initialize_discover_invoke_and_server_errors():
    async def scenario():
        async with Session("duplicate-work", "specification") as session:
            assert session.protocol_version
            assert session.server_name == "synthetic-specification"
            assert set(session.tools) == {"search_specs", "get_requirement", "get_schema_version"}
            response = await session.call(
                "get_requirement", {"record_id": "R-duplicate-work", "version": "1"}
            )
            assert response["status"] == "ok"
            assert response["source_id"] == "R-duplicate-work"
            assert response["version"] == "1"
            for args, expected in [
                ({"record_id": "missing", "version": "1"}, "missing"),
                ({"record_id": "R-duplicate-work", "version": "0"}, "stale"),
                ({"record_id": "R-scheduled-delivery", "version": "1"}, "denied"),
            ]:
                assert (await session.call("get_requirement", args))["status"] == expected
            assert (await session.call("search_specs", {"query": "x" * 257}))["status"] == "invalid"
            assert (
                await session.call("get_requirement", {"record_id": "../secret", "version": "1"})
            )["status"] == "invalid"
            assert [x["sequence"] for x in session.trace] == list(range(1, len(session.trace) + 1))
        async with Session("duplicate-work", "evidence") as session:
            assert set(session.tools) == {
                "get_issue",
                "read_sanitized_log",
                "get_expected_transition",
            }
            for name, prefix in [
                ("get_issue", "I"),
                ("read_sanitized_log", "L"),
                ("get_expected_transition", "T"),
            ]:
                result = await session.call(
                    name, {"record_id": prefix + "-duplicate-work", "version": "1"}
                )
                assert result["status"] == "ok"

    asyncio.run(scenario())


def test_restart_timeout_and_no_cross_task_leakage():
    async def scenario():
        async with Session("duplicate-work", "evidence", response_delay=0.2) as session:
            with pytest.raises(TimeoutError):
                await session.call(
                    "get_issue", {"record_id": "I-duplicate-work", "version": "1"}, timeout=0.01
                )
            assert session.trace[-1]["status"] == "timeout"
        async with Session("duplicate-work", "evidence") as restarted:
            assert (
                await restarted.call("get_issue", {"record_id": "I-duplicate-work", "version": "1"})
            )["status"] == "ok"
        async with Session("scheduled-delivery", "evidence") as other:
            assert (
                await other.call("get_issue", {"record_id": "I-duplicate-work", "version": "1"})
            )["status"] == "denied"
            assert len(other.trace) == 1

    asyncio.run(scenario())


@pytest.mark.parametrize("task", TASKS)
def test_behavior_controls_and_alternative_solution(task, tmp_path):
    outcomes = {}
    for variant in ["baseline", "reference", "alternative", "wrong-1", "wrong-2"]:
        result = asyncio.run(run_attempt(task, variant, tmp_path / variant))
        outcomes[variant] = result["functional"]["passed"]
        assert result["mcp_usage"]["passed"] == (variant != "baseline")
        assert result["functional"]["checks"]
        assert all(x["exit_code"] in [0, 1] for x in result["functional"]["checks"])
        for filename in [
            "manifest.json",
            "result.json",
            "test_results.json",
            "changed_files.json",
            "mcp_tool_trace.jsonl",
            "reproduction.md",
            "review.md",
        ]:
            assert (tmp_path / variant / filename).is_file()
    assert outcomes == {
        "baseline": False,
        "reference": True,
        "alternative": True,
        "wrong-1": False,
        "wrong-2": False,
    }
    # All incorrect controls must fail a named behavioral assertion, not setup/import/timeout.
    for variant in ["baseline", "wrong-1", "wrong-2"]:
        report = json.loads((tmp_path / variant / "test_results.json").read_text())
        assert any(x["status"] == "assertion_failed" for x in report["checks"])
        assert all(x["status"] != "infrastructure_error" for x in report["checks"])


def test_workspace_excludes_verifier_and_blocks_bad_paths(tmp_path):
    with Workspace("duplicate-work") as work:
        assert sorted(
            str(p.relative_to(work.path)) for p in work.path.rglob("*") if p.is_file()
        ) == ["README.md", "public_tests.py", "solution.py"]
        for name in ["../solution.py", "/tmp/solution.py", "README.md", ".git/config"]:
            with pytest.raises(ValueError):
                work.apply({name: "bad"})
        target = tmp_path / "outside.py"
        target.write_text("original")
        (work.path / "solution.py").unlink()
        (work.path / "solution.py").symlink_to(target)
        with pytest.raises(ValueError):
            work.apply({"solution.py": "escaped"})
        assert target.read_text() == "original"


def test_schema_only_calls_and_tampered_references_do_not_pass(tmp_path):
    async def scenario():
        async with Session("duplicate-work", "specification") as session:
            await session.call("get_schema_version", {})
            assert not meaningful_usage("duplicate-work", session.trace, [], ["solution.py"])[
                "passed"
            ]
        result = await run_attempt("duplicate-work", "reference", tmp_path / "valid")
        assert result["functional"]["passed"]
        trace = [
            json.loads(x)
            for x in (tmp_path / "valid/mcp_tool_trace.jsonl").read_text().splitlines()
        ]
        refs = json.loads((tmp_path / "valid/changed_files.json").read_text())["source_references"]
        refs[0]["version"] = "old"
        assert not meaningful_usage("duplicate-work", trace, refs, ["solution.py"])["passed"]
        refs[0]["version"] = "1"
        refs[0]["path"] = "verifier.py"
        assert not meaningful_usage("duplicate-work", trace, refs, ["solution.py"])["passed"]

    asyncio.run(scenario())


def test_boundary_verifier_rejects_network_imports():
    from mcp_rl_lab.protocol_bench.acceptance import boundary

    for source in [
        "import urllib.request",
        "from socket import socket",
        "import http.client",
        "__import__('urllib.request')",
    ]:
        with pytest.raises(AssertionError):
            boundary(None, "no-vendor-or-network-dependency", source)


def test_discovery_failure_closes_entered_client(monkeypatch):
    from types import SimpleNamespace

    from mcp_rl_lab.protocol_bench import client as module

    exits = []

    class BrokenDiscovery:
        protocol_version = "test"
        server_info = SimpleNamespace(name="synthetic-test")

        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            exits.append(True)

        async def list_tools(self):
            raise ValueError("controlled discovery failure")

    monkeypatch.setattr(module, "Client", BrokenDiscovery)

    async def scenario():
        session = Session("duplicate-work", "specification")
        with pytest.raises(ValueError, match="controlled discovery failure"):
            await session.__aenter__()
        assert exits == [True]
        assert session.errors.closed
        assert not Path(session.home_name).exists()

    asyncio.run(scenario())
