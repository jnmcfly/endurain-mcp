"""MCP tools for Endurain user endpoints."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from endurain_mcp.client import EndurainClient


def register(mcp: FastMCP, client: EndurainClient) -> None:
    """Register all user-related MCP tools."""

    @mcp.tool()
    def get_me() -> dict:
        """
        Return the profile of the currently authenticated user.

        Returns:
            UsersMe object with full profile details including id, name, username, email, etc.
        """
        return client.get("/profile")

    @mcp.tool()
    def list_users(page_number: int = 1, num_records: int = 20) -> list[dict]:
        """
        List all users (admin only, paginated).

        Args:
            page_number: Page index starting at 1.
            num_records: Records per page.

        Returns:
            List of UsersRead objects.
        """
        result = client.get(f"/users/page_number/{page_number}/num_records/{num_records}")
        if isinstance(result, dict):
            return result.get("records", [])
        return result or []

    @mcp.tool()
    def get_user(user_id: int) -> dict:
        """
        Get a user by ID.

        Args:
            user_id: Numeric user ID.

        Returns:
            UsersRead object.
        """
        return client.get(f"/users/id/{user_id}")

    @mcp.tool()
    def create_user(
        name: str,
        username: str,
        email: str,
        password: str,
        access_type: str = "regular",
        active: bool = True,
    ) -> dict:
        """
        Create a new user account (admin only).

        access_type values: "regular", "admin"

        Args:
            name: Full display name (required).
            username: Unique username (alphanumeric, dots, hyphens, underscores).
            email: Email address.
            password: Initial password.
            access_type: Access level ("regular" or "admin").
            active: Whether the account is active.

        Returns:
            Created UsersRead object.
        """
        return client.post(
            "/users",
            json={
                "name": name,
                "username": username,
                "email": email,
                "password": password,
                "access_type": access_type,
                "active": active,
            },
        )

    @mcp.tool()
    def edit_user(
        user_id: int,
        name: str | None = None,
        email: str | None = None,
        username: str | None = None,
        preferred_language: str | None = None,
        units: str | None = None,
        city: str | None = None,
        gender: str | None = None,
        access_type: str | None = None,
        active: bool | None = None,
    ) -> dict:
        """
        Edit an existing user. Only the fields you supply will be changed.

        Args:
            user_id: ID of the user to edit.
            name: New display name.
            email: New email address.
            username: New username.
            preferred_language: Language code (e.g. "us", "de").
            units: "metric" or "imperial".
            city: City name.
            gender: "male", "female", or "other".
            access_type: "regular" or "admin".
            active: Account active status.

        Returns:
            Updated UsersRead object.
        """
        # Fetch current values to satisfy all required fields
        current = client.get(f"/users/id/{user_id}")
        payload = {
            "id": user_id,
            "name": current.get("name"),
            "username": current.get("username"),
            "email": current.get("email"),
            "access_type": current.get("access_type"),
            "active": current.get("active"),
        }
        for key, val in {
            "name": name,
            "email": email,
            "username": username,
            "preferred_language": preferred_language,
            "units": units,
            "city": city,
            "gender": gender,
            "access_type": access_type,
            "active": active,
        }.items():
            if val is not None:
                payload[key] = val
        return client.put(f"/users/{user_id}", json=payload)

    @mcp.tool()
    def delete_user(user_id: int) -> dict:
        """
        Delete a user account (admin only).

        Args:
            user_id: ID to delete.

        Returns:
            Confirmation message.
        """
        return client.delete(f"/users/{user_id}")

    @mcp.tool()
    def list_sessions() -> list[dict]:
        """
        List active sessions for the authenticated user.

        Returns:
            List of session objects.
        """
        return client.get("/profile/sessions") or []

    @mcp.tool()
    def delete_session(session_id: str) -> dict:
        """
        Revoke a specific session.

        Args:
            session_id: UUID of the session to revoke.

        Returns:
            Confirmation message.
        """
        return client.delete(f"/profile/sessions/{session_id}")

    @mcp.tool()
    def list_followers(user_id: int | None = None) -> list[dict]:
        """
        List followers of a user.

        Args:
            user_id: User ID (defaults to authenticated user).

        Returns:
            List of follower objects.
        """
        uid = user_id or _me_id(client)
        return client.get(f"/followers/user/{uid}/followers/all") or []

    @mcp.tool()
    def list_following(user_id: int | None = None) -> list[dict]:
        """
        List users followed by a user.

        Args:
            user_id: User ID (defaults to authenticated user).

        Returns:
            List of following objects.
        """
        uid = user_id or _me_id(client)
        return client.get(f"/followers/user/{uid}/following/all") or []

    @mcp.tool()
    def follow_user(user_id: int) -> dict:
        """
        Follow a user.

        Args:
            user_id: ID of the user to follow.

        Returns:
            Confirmation message.
        """
        return client.post(f"/followers/create/targetUser/{user_id}")

    @mcp.tool()
    def unfollow_user(user_id: int) -> dict:
        """
        Unfollow a user.

        Args:
            user_id: ID of the user to unfollow.

        Returns:
            Confirmation message.
        """
        return client.delete(f"/followers/delete/following/targetUser/{user_id}")


def _me_id(client: EndurainClient) -> int:
    """Helper: return the authenticated user's ID via /profile."""
    me = client.get("/profile")
    return me["id"]
