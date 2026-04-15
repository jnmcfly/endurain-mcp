"""Entry point for `uvx endurain-mcp` / `python -m endurain_mcp`."""

from endurain_mcp.client import EndurainClient
from endurain_mcp.server import create_server


def main() -> None:
    """Initialise the Endurain client and run the MCP server over stdio."""
    client = EndurainClient()
    mcp = create_server(client)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
