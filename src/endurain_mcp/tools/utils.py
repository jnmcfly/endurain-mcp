"""Shared helpers for tool modules."""

from __future__ import annotations

from endurain_mcp.client import EndurainClient


def me_id(client: EndurainClient) -> int:
    """Return the authenticated user's ID via /profile."""
    me = client.get("/profile")
    return me["id"]
