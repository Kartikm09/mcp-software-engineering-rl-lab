from typing import Literal

from mcp.server.mcpserver import MCPServer

from mcp_servers.runtime import content

mcp = MCPServer("allowlisted-context-database")


@mcp.tool()
def query_context(
    query_name: Literal["task_constraints", "failure_history"],
) -> dict[str, object]:
    """Run one predefined read-only query against the synthetic context database."""
    return content("database", "query_context", {"query_name": query_name})


if __name__ == "__main__":
    mcp.run()
