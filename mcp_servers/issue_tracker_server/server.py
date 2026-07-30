from mcp.server.mcpserver import MCPServer

from mcp_servers.runtime import content

mcp = MCPServer("local-issue-tracker")


@mcp.tool()
def get_issue(task_id: str) -> dict[str, object]:
    """Return the synthetic issue title and body for a task."""
    return content("issue_tracker", "get_issue", {"task_id": task_id})


@mcp.tool()
def get_acceptance_criteria(task_id: str) -> dict[str, object]:
    """Return acceptance criteria intentionally omitted from the initial prompt."""
    return content("issue_tracker", "get_acceptance_criteria", {"task_id": task_id})


if __name__ == "__main__":
    mcp.run()
