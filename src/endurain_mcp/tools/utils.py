"""Shared helpers for tool modules."""

from __future__ import annotations

from endurain_mcp.client import EndurainClient


def me_id(client: EndurainClient) -> int:
    """Return the authenticated user's ID via /profile."""
    me = client.get("/profile")
    return me["id"]


def format_pace(pace_s_per_m: float | None) -> str | None:
    """Convert pace in seconds/metre to a 'mm:ss /km' string."""
    if pace_s_per_m is None:
        return None
    total_s = round(pace_s_per_m * 1000)
    return f"{total_s // 60}:{total_s % 60:02d} /km"
