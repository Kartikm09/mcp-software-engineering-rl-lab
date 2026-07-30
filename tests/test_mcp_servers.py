from __future__ import annotations

from mcp_rl_lab.config import Settings
from mcp_servers.toolkit import LocalToolRegistry


def test_repository_server_lists_and_reads_bounded_files(python_task) -> None:
    registry = LocalToolRegistry(python_task)
    listing = registry.call("repository", "list_files", {"path": "."})
    content = registry.call("repository", "read_file", {"path": "retry.py"})
    assert listing.ok and listing.content["files"] == ["retry.py"]
    assert content.ok and "backoff_delay" in content.content["text"]


def test_servers_return_structured_errors(python_task) -> None:
    registry = LocalToolRegistry(python_task)
    unknown = registry.call("repository", "not_a_tool", {})
    escaped = registry.call("repository", "read_file", {"path": "../golden/solution.patch"})
    database = registry.call("database", "query_context", {"query_name": "drop_everything"})
    assert (unknown.ok, unknown.error_code) == (False, "unknown_tool")
    assert not escaped.ok and escaped.error_code == "valueerror"
    assert not database.ok and database.error_code == "valueerror"


def test_issue_documentation_and_database_tools_return_task_context(python_task) -> None:
    registry = LocalToolRegistry(python_task)
    issue = registry.call("issue_tracker", "get_acceptance_criteria", {})
    docs = registry.call("documentation", "search_docs", {"query": "backoff"})
    database = registry.call("database", "query_context", {"query_name": "failure_history"})
    assert issue.ok and len(issue.content["acceptance_criteria"]) >= 2
    assert docs.ok and docs.content["matches"]
    assert database.ok and database.content["rows"]


def test_test_runner_captures_expected_baseline_failure(python_task) -> None:
    registry = LocalToolRegistry(
        python_task, Settings(command_timeout_seconds=20, max_output_bytes=100_000)
    )
    result = registry.call("test_runner", "run_public_tests", {})
    assert result.ok
    assert result.content["commands"][0]["exit_code"] != 0


def test_official_mcp_server_modules_import() -> None:
    from mcp_servers.benchmark_server import server as benchmark_server
    from mcp_servers.database_server import server as database_server
    from mcp_servers.documentation_server import server as documentation_server
    from mcp_servers.issue_tracker_server import server as issue_tracker_server
    from mcp_servers.repository_server import server as repository_server
    from mcp_servers.test_runner_server import server as test_runner_server

    modules = [
        benchmark_server,
        database_server,
        documentation_server,
        issue_tracker_server,
        repository_server,
        test_runner_server,
    ]
    assert all(hasattr(module, "mcp") for module in modules)
