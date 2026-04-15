"""MCP server factory for Endurain."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from endurain_mcp.client import EndurainClient
from endurain_mcp.tools import activities, gears, health, profile, users


def create_server(client: EndurainClient) -> FastMCP:
    """
    Build and return a fully wired FastMCP server instance.

    All domain tool modules are registered against the provided client.

    Args:
        client: Authenticated Endurain API client.

    Returns:
        Configured FastMCP server ready to run.
    """
    mcp = FastMCP(name="endurain")

    activities.register(mcp, client)
    gears.register(mcp, client)
    health.register(mcp, client)
    profile.register(mcp, client)
    users.register(mcp, client)

    return mcp
