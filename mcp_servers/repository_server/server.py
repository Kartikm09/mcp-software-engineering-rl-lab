from mcp.server.mcpserver import MCPServer

from mcp_servers.runtime import content

mcp = MCPServer("local-repository")


@mcp.tool()
def list_files(path: str = ".") -> dict[str, object]:
    """List bounded files below the task baseline root."""
    return content("repository", "list_files", {"path": path})


@mcp.tool()
def read_file(path: str) -> dict[str, object]:
    """Read one UTF-8 file below the task baseline root."""
    return content("repository", "read_file", {"path": path})


@mcp.tool()
def search_text(query: str) -> dict[str, object]:
    """Search literal text across bounded baseline files."""
    return content("repository", "search_text", {"query": query})


if __name__ == "__main__":
    mcp.run()
