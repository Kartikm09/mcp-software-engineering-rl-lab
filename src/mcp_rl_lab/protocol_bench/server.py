"""Two independently scoped local MCP server processes using the official SDK."""

import argparse
import asyncio
from typing import Annotated, Literal

from mcp.server import MCPServer
from pydantic import BaseModel, ConfigDict, Field

from .catalog import TASKS, load

Identifier = Annotated[str, Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")]
Version = Annotated[str, Field(min_length=1, max_length=16)]
Query = Annotated[str, Field(min_length=1, max_length=256)]


class Reply(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: Literal["ok", "missing", "stale", "denied"]
    source_id: str = Field(max_length=80)
    version: str = Field(max_length=16)
    task_id: str = Field(max_length=40)
    text: str = Field(max_length=4096)
    classification: Literal["synthetic"] = "synthetic"


def build_server(task_id: str, kind: str, response_delay: float = 0) -> MCPServer:
    # Delay is server-launch test configuration, never a callable tool argument.
    if not 0 <= response_delay <= 1:
        raise ValueError("delay must be at most one second")
    corpus = load(task_id)
    server = MCPServer("synthetic-" + kind)

    async def get(record_id, version, prefix):
        if response_delay:
            await asyncio.sleep(response_delay)
        known = any(record_id == f"{p}-{task}" for p in ["R", "I", "L", "T"] for task in TASKS)
        record = corpus["records"].get(record_id)
        if record is None or not record_id.startswith(prefix + "-"):
            status = "denied" if known else "missing"
            return Reply(
                status=status,
                source_id=record_id,
                version="1",
                task_id=task_id,
                text="Record unavailable in this task/tool scope",
            )
        if version != record["version"]:
            return Reply(
                status="stale",
                source_id=record_id,
                version=record["version"],
                task_id=task_id,
                text="Request the advertised current version",
            )
        return Reply(status="ok", **record)

    if kind == "specification":

        @server.tool()
        async def search_specs(query: Query) -> list[Reply]:
            """Search the one task-scoped synthetic requirement; returns at most one result."""
            record = corpus["records"]["R-" + task_id]
            if query.casefold() not in record["text"].casefold():
                return []
            return [Reply(status="ok", **record)]

        @server.tool()
        async def get_requirement(record_id: Identifier, version: Version) -> Reply:
            """Read a bounded requirement at an explicit document version."""
            return await get(record_id, version, "R")

        @server.tool()
        def get_schema_version() -> Reply:
            """Advertise the version without satisfying task evidence requirements."""
            return Reply(
                status="ok",
                source_id="schema",
                version="1",
                task_id=task_id,
                text="schema=1; document version=1",
            )
    elif kind == "evidence":

        @server.tool()
        async def get_issue(record_id: Identifier, version: Version) -> Reply:
            """Read one synthetic incident in this task scope."""
            return await get(record_id, version, "I")

        @server.tool()
        async def read_sanitized_log(record_id: Identifier, version: Version) -> Reply:
            """Read synthetic incident text with no real user or provider logs."""
            return await get(record_id, version, "L")

        @server.tool()
        async def get_expected_transition(record_id: Identifier, version: Version) -> Reply:
            """Read the documented state or data transformation contract."""
            return await get(record_id, version, "T")
    else:
        raise ValueError("unknown server kind")
    return server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task", choices=TASKS)
    parser.add_argument("server", choices=["specification", "evidence"])
    parser.add_argument("--response-delay", type=float, default=0)
    args = parser.parse_args()
    build_server(args.task, args.server, args.response_delay).run(transport="stdio")


if __name__ == "__main__":
    main()
