"""Real initialization/discovery/tool calls, captured without private model reasoning."""

import hashlib
import json
import os
import sys
import tempfile
from contextlib import ExitStack, contextmanager
from datetime import UTC, datetime
from pathlib import Path

from mcp import Client
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.shared.exceptions import MCPError

from .catalog import load, task_root


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


@contextmanager
def error_stream():
    with tempfile.TemporaryFile(mode="w+") as stream:
        yield stream


class Session:
    def __init__(self, task_id, kind, response_delay=0):
        task_root(task_id)
        self.task_id, self.kind = task_id, kind
        self.response_delay = response_delay
        self.trace = []

    async def __aenter__(self):
        self.stack = ExitStack()
        self.home_name = self.stack.enter_context(
            tempfile.TemporaryDirectory(prefix="synthetic-mcp-home-")
        )
        self.errors = self.stack.enter_context(error_stream())
        source = str(Path(__file__).resolve().parents[2])
        params = StdioServerParameters(
            command=sys.executable,
            args=[
                "-m",
                "mcp_rl_lab.protocol_bench.server",
                self.task_id,
                self.kind,
                "--response-delay",
                str(self.response_delay),
            ],
            cwd=self.home_name,
            env={
                "HOME": self.home_name,
                "USER": "synthetic",
                "LOGNAME": "synthetic",
                "PATH": str(Path(sys.executable).parent) + os.pathsep + os.defpath,
                "PYTHONPATH": source,
                "PYTHONNOUSERSITE": "1",
                "PYTHONDONTWRITEBYTECODE": "1",
            },
        )
        # Legacy mode explicitly exercises initialize/initialized through JSON-RPC stdio.
        self.client = Client(
            stdio_client(params, errlog=self.errors), mode="legacy", read_timeout_seconds=60
        )
        entered = False
        try:
            await self.client.__aenter__()
            entered = True
            self.protocol_version = self.client.protocol_version
            self.server_name = self.client.server_info.name
            discovery = await self.client.list_tools()
            self.tools = {tool.name: tool.input_schema for tool in discovery.tools}
            return self
        except BaseException:
            try:
                if entered:
                    await self.client.__aexit__(None, None, None)
            finally:
                self.stack.close()
            raise

    async def __aexit__(self, *args):
        try:
            return await self.client.__aexit__(*args)
        finally:
            self.stack.close()

    async def call(self, name, arguments, timeout=10):
        entry = {
            "sequence": len(self.trace) + 1,
            "server": self.kind,
            "task_id": self.task_id,
            "tool": name,
            "arguments": arguments,
            "timestamp": datetime.now(UTC).isoformat(),
            "protocol_version": self.protocol_version,
        }
        try:
            result = await self.client.call_tool(name, arguments, read_timeout_seconds=timeout)
            if result.is_error:
                response = {
                    "status": "invalid",
                    "error": "SDK rejected tool arguments or invocation",
                }
            else:
                response = result.structured_content
                if response is None:
                    response = {"status": "invalid", "error": "missing structured response"}
            entry.update(
                status=response.get("status", "ok"),
                response=response,
                version=response.get("version"),
                response_sha256=digest(response),
            )
            return response
        except MCPError as error:
            if "timed out" in str(error).lower() or "timeout" in str(error).lower():
                entry.update(status="timeout", version=None)
                raise TimeoutError("MCP request timed out") from error
            entry.update(status="protocol_error", version=None)
            raise
        finally:
            self.trace.append(entry)


def meaningful_usage(task_id, trace, references, changed_paths):
    corpus = load(task_id)
    required = set(corpus["required_sources"])
    valid = set()
    problems = []
    # Only session-captured successful tools from this task, with untampered responses, qualify.
    evidence = {}
    for entry in trace:
        reply = entry.get("response", {})
        expected_tool = (
            "get_requirement" if reply.get("source_id", "").startswith("R-") else "get_issue"
        )
        if (
            entry.get("task_id") == task_id
            and entry.get("status") == "ok"
            and entry.get("tool") == expected_tool
            and entry.get("server")
            == ("specification" if expected_tool == "get_requirement" else "evidence")
            and reply.get("version") == corpus["version"]
            and reply.get("task_id") == task_id
            and entry.get("response_sha256") == digest(reply)
        ):
            evidence[(reply.get("source_id"), reply.get("version"))] = entry
    for ref in references:
        key = (ref.get("source_id"), ref.get("version"))
        entry = evidence.get(key)
        if (
            entry
            and ref.get("path") in changed_paths
            and ref.get("response_sha256") == entry["response_sha256"]
            and isinstance(ref.get("decision"), str)
            and len(ref["decision"].strip()) >= 20
        ):
            valid.add(key[0])
        else:
            problems.append("unlinked, stale or invalid source reference")
    missing = sorted(required - valid)
    return {
        "passed": not missing and not problems,
        "required_sources": sorted(required),
        "linked_sources": sorted(valid),
        "missing": missing,
        "problems": problems,
        "limitation": "Checks retrieval/reference linkage; does not prove model understanding.",
    }
