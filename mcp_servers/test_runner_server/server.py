from mcp.server.mcpserver import MCPServer

from mcp_servers.runtime import content

mcp = MCPServer("allowlisted-test-runner")


@mcp.tool()
def run_public_tests() -> dict[str, object]:
    """Run only the task's declared public test commands in a temporary workspace."""
    return content("test_runner", "run_public_tests", {})


if __name__ == "__main__":
    mcp.run()
