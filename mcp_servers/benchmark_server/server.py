from mcp.server.mcpserver import MCPServer

from mcp_servers.runtime import content

mcp = MCPServer("allowlisted-benchmark-runner")


@mcp.tool()
def run_baseline_benchmark() -> dict[str, object]:
    """Run only the benchmark commands declared by the active task."""
    return content("benchmark", "run_baseline_benchmark", {})


if __name__ == "__main__":
    mcp.run()
