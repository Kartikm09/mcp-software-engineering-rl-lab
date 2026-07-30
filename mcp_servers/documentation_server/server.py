from mcp.server.mcpserver import MCPServer

from mcp_servers.runtime import content

mcp = MCPServer("local-documentation")


@mcp.tool()
def search_docs(query: str) -> dict[str, object]:
    """Search synthetic task documentation by literal text."""
    return content("documentation", "search_docs", {"query": query})


@mcp.tool()
def read_doc(name: str) -> dict[str, object]:
    """Read one Markdown document from the local documentation fixture."""
    return content("documentation", "read_doc", {"name": name})


if __name__ == "__main__":
    mcp.run()
