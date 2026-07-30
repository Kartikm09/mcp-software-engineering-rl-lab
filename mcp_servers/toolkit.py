"""Narrow local tool implementations shared by MCP transports and tests."""

from __future__ import annotations

import json
import re
import sqlite3
from collections.abc import Callable
from pathlib import Path

from mcp_rl_lab.config import Settings
from mcp_rl_lab.models import ToolResult
from mcp_rl_lab.process import run_command
from mcp_rl_lab.safety import safe_relative_path
from mcp_rl_lab.task_loader import TaskPackage
from mcp_rl_lab.workspace_manager import CandidateWorkspace

LAB_ROOT = Path(__file__).resolve().parents[1]


class LocalToolRegistry:
    """Dispatch deterministic tools through one structured result contract."""

    servers = [
        "repository",
        "issue_tracker",
        "documentation",
        "test_runner",
        "benchmark",
        "database",
    ]

    def __init__(self, task: TaskPackage, settings: Settings | None = None) -> None:
        self.task = task
        self.settings = settings or Settings.from_env()
        self._tools: dict[tuple[str, str], Callable[[dict[str, object]], dict[str, object]]] = {
            ("repository", "list_files"): self._list_files,
            ("repository", "read_file"): self._read_file,
            ("repository", "search_text"): self._search_text,
            ("issue_tracker", "get_issue"): self._get_issue,
            ("issue_tracker", "get_acceptance_criteria"): self._get_acceptance_criteria,
            ("documentation", "search_docs"): self._search_docs,
            ("documentation", "read_doc"): self._read_doc,
            ("test_runner", "run_public_tests"): self._run_public_tests,
            ("benchmark", "run_baseline_benchmark"): self._run_baseline_benchmark,
            ("database", "query_context"): self._query_context,
        }

    def call(self, server: str, tool: str, arguments: dict[str, object]) -> ToolResult:
        handler = self._tools.get((server, tool))
        if handler is None:
            return ToolResult(
                ok=False,
                error_code="unknown_tool",
                error_message=f"unknown tool: {server}.{tool}",
            )
        try:
            return ToolResult(ok=True, content=handler(arguments))
        except (ValueError, FileNotFoundError, KeyError, sqlite3.Error) as error:
            return ToolResult(
                ok=False,
                error_code=type(error).__name__.lower(),
                error_message=str(error),
            )

    @property
    def baseline_root(self) -> Path:
        return self.task.path(self.task.manifest.baseline_path)

    def _bounded_path(self, value: object, root: Path) -> Path:
        relative = safe_relative_path(str(value))
        candidate = (root / Path(*relative.parts)).resolve()
        if not candidate.is_relative_to(root.resolve()):
            raise ValueError("path escapes tool root")
        return candidate

    def _list_files(self, arguments: dict[str, object]) -> dict[str, object]:
        relative = str(arguments.get("path", "."))
        root = (
            self._bounded_path(relative, self.baseline_root)
            if relative != "."
            else self.baseline_root
        )
        if not root.is_dir():
            raise FileNotFoundError(relative)
        files = sorted(
            str(path.relative_to(self.baseline_root)) for path in root.rglob("*") if path.is_file()
        )
        return {"files": files[:500], "truncated": len(files) > 500}

    def _read_file(self, arguments: dict[str, object]) -> dict[str, object]:
        path = self._bounded_path(arguments["path"], self.baseline_root)
        if not path.is_file():
            raise FileNotFoundError(str(arguments["path"]))
        if path.stat().st_size > 200_000:
            raise ValueError("file exceeds read limit")
        return {
            "path": str(path.relative_to(self.baseline_root)),
            "text": path.read_text(encoding="utf-8"),
        }

    def _search_text(self, arguments: dict[str, object]) -> dict[str, object]:
        query = str(arguments["query"])
        if not query or len(query) > 100:
            raise ValueError("query must contain 1 to 100 characters")
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        matches: list[dict[str, object]] = []
        for path in sorted(self.baseline_root.rglob("*")):
            if not path.is_file() or path.stat().st_size > 200_000:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for number, line in enumerate(text.splitlines(), start=1):
                if pattern.search(line):
                    matches.append(
                        {
                            "path": str(path.relative_to(self.baseline_root)),
                            "line": number,
                            "text": line[:300],
                        }
                    )
                    if len(matches) == 100:
                        return {"matches": matches, "truncated": True}
        return {"matches": matches, "truncated": False}

    def _issues(self) -> dict[str, object]:
        return json.loads((LAB_ROOT / "fixtures/issues/issues.json").read_text(encoding="utf-8"))

    def _get_issue(self, arguments: dict[str, object]) -> dict[str, object]:
        task_id = str(arguments.get("task_id", self.task.manifest.id))
        issue = self._issues().get(task_id)
        if issue is None:
            raise KeyError(task_id)
        return {"task_id": task_id, "title": issue["title"], "body": issue["body"]}

    def _get_acceptance_criteria(self, arguments: dict[str, object]) -> dict[str, object]:
        task_id = str(arguments.get("task_id", self.task.manifest.id))
        issue = self._issues().get(task_id)
        if issue is None:
            raise KeyError(task_id)
        return {"task_id": task_id, "acceptance_criteria": issue["acceptance_criteria"]}

    @property
    def docs_root(self) -> Path:
        return LAB_ROOT / "fixtures/docs"

    def _search_docs(self, arguments: dict[str, object]) -> dict[str, object]:
        query = str(arguments["query"])
        if not query or len(query) > 100:
            raise ValueError("query must contain 1 to 100 characters")
        matches: list[dict[str, object]] = []
        for path in sorted(self.docs_root.glob("*.md")):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if query.casefold() in line.casefold():
                    matches.append({"document": path.name, "line": number, "text": line})
        return {"matches": matches[:100], "truncated": len(matches) > 100}

    def _read_doc(self, arguments: dict[str, object]) -> dict[str, object]:
        path = self._bounded_path(arguments["name"], self.docs_root)
        if not path.is_file() or path.suffix != ".md":
            raise FileNotFoundError(str(arguments["name"]))
        return {"name": path.name, "text": path.read_text(encoding="utf-8")}

    def _run_public_tests(self, _arguments: dict[str, object]) -> dict[str, object]:
        with CandidateWorkspace(self.task) as workspace:
            evidence = []
            for command in self.task.manifest.commands.public:
                result = run_command(
                    command,
                    workspace.path,
                    timeout_seconds=self.task.manifest.timeout_seconds,
                    max_output_bytes=self.settings.max_output_bytes,
                )
                evidence.append(result.model_dump(mode="json"))
                if result.exit_code != 0:
                    break
        return {"suite": "public", "commands": evidence}

    def _run_baseline_benchmark(self, _arguments: dict[str, object]) -> dict[str, object]:
        if not self.task.manifest.commands.benchmark:
            return {"available": False, "reason": "task has no benchmark command"}
        with CandidateWorkspace(self.task) as workspace:
            evidence = [
                run_command(
                    command,
                    workspace.path,
                    timeout_seconds=self.task.manifest.timeout_seconds,
                    max_output_bytes=self.settings.max_output_bytes,
                ).model_dump(mode="json")
                for command in self.task.manifest.commands.benchmark
            ]
        return {"available": True, "commands": evidence}

    def _query_context(self, arguments: dict[str, object]) -> dict[str, object]:
        query_name = str(arguments["query_name"])
        queries = {
            "task_constraints": (
                "SELECT key, value FROM task_context WHERE task_id = ? ORDER BY key"
            ),
            "failure_history": (
                "SELECT category, detail FROM failure_history WHERE task_id = ? ORDER BY category"
            ),
        }
        if query_name not in queries:
            raise ValueError("query_name is not allowlisted")
        connection = sqlite3.connect(":memory:")
        connection.executescript(
            (LAB_ROOT / "fixtures/database/context.sql").read_text(encoding="utf-8")
        )
        rows = connection.execute(queries[query_name], (self.task.manifest.id,)).fetchall()
        connection.close()
        return {"query_name": query_name, "rows": [list(row) for row in rows]}
