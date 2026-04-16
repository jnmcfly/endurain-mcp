"""MCP tools for Endurain activity endpoints."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from endurain_mcp.client import EndurainClient


def register(mcp: FastMCP, client: EndurainClient) -> None:
    """Register all activity-related MCP tools."""

    @mcp.tool()
    def list_activities(
        page_number: int = 1,
        num_records: int = 20,
        user_id: int | None = None,
        activity_type: int | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        name_search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> list[dict]:
        """
        List activities with optional filters and pagination.

        Args:
            page_number: Page index, starting at 1.
            num_records: Number of records per page (max 100).
            user_id: Filter by user ID (defaults to the authenticated user).
            activity_type: Filter by numeric activity type.
            start_date: ISO-8601 start date filter (YYYY-MM-DD).
            end_date: ISO-8601 end date filter (YYYY-MM-DD).
            name_search: Substring search on activity name.
            sort_by: Field to sort by (e.g. "date", "distance").
            sort_order: "asc" or "desc".

        Returns:
            List of activity objects.
        """
        params: dict = {}
        if activity_type is not None:
            params["type"] = activity_type
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if name_search:
            params["name_search"] = name_search
        if sort_by:
            params["sort_by"] = sort_by
        if sort_order:
            params["sort_order"] = sort_order

        uid = user_id or _me_id(client)
        return (
            client.get(
                f"/activities/user/{uid}/page_number/{page_number}/num_records/{num_records}",
                params=params,
            )
            or []
        )

    @mcp.tool()
    def get_activity(activity_id: int) -> dict:
        """
        Get a single activity by ID.

        Args:
            activity_id: The numeric ID of the activity.

        Returns:
            Activity object.
        """
        return client.get(f"/activities/{activity_id}")

    @mcp.tool()
    def get_activities_count(
        activity_type: int | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
        name_search: str | None = None,
    ) -> int:
        """
        Return the total count of activities for the authenticated user.

        Args:
            activity_type: Optional numeric type filter.
            start_date: ISO-8601 start date (YYYY-MM-DD).
            end_date: ISO-8601 end date (YYYY-MM-DD).
            name_search: Substring search on activity name.

        Returns:
            Integer count.
        """
        params: dict = {}
        if activity_type is not None:
            params["type"] = activity_type
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if name_search:
            params["name_search"] = name_search
        return client.get("/activities/number", params=params)

    @mcp.tool()
    def get_activities_this_week(user_id: int | None = None) -> dict | None:
        """
        Get distance totals for the current calendar week.

        Args:
            user_id: User ID (defaults to authenticated user).

        Returns:
            ActivityDistances object with per-sport distances.
        """
        uid = user_id or _me_id(client)
        return client.get(f"/activities/user/{uid}/thisweek/distances")

    @mcp.tool()
    def get_activities_this_month(user_id: int | None = None) -> dict | None:
        """
        Get distance totals for the current calendar month.

        Args:
            user_id: User ID (defaults to authenticated user).

        Returns:
            ActivityDistances object.
        """
        uid = user_id or _me_id(client)
        return client.get(f"/activities/user/{uid}/thismonth/distances")

    @mcp.tool()
    def get_activities_week(week_number: int, user_id: int | None = None) -> list[dict]:
        """
        Get activities for a specific week relative to today.

        Args:
            week_number: Number of weeks ago (0 = current week, 1 = last week, …).
            user_id: User ID (defaults to authenticated user).

        Returns:
            List of activity objects.
        """
        uid = user_id or _me_id(client)
        return client.get(f"/activities/user/{uid}/week/{week_number}") or []

    @mcp.tool()
    def get_activity_types() -> dict | None:
        """
        Return a dict of distinct activity types used by the authenticated user.

        Returns:
            Dict mapping activity type integer to label.
        """
        return client.get("/activities/types")

    @mcp.tool()
    def edit_activity(
        activity_id: int,
        name: str | None = None,
        description: str | None = None,
        visibility: int | None = None,
        gear_id: int | None = None,
    ) -> dict:
        """
        Edit an existing activity.

        Args:
            activity_id: ID of the activity to edit.
            name: New name.
            description: New description.
            visibility: New visibility level (0=private, 1=followers, 2=public).
            gear_id: Associated gear ID.

        Returns:
            Confirmation message.
        """
        payload: dict = {"id": activity_id}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if visibility is not None:
            payload["visibility"] = visibility
        if gear_id is not None:
            payload["gear_id"] = gear_id
        return client.put("/activities/edit", json=payload)

    @mcp.tool()
    def delete_activity(activity_id: int) -> dict:
        """
        Delete an activity permanently.

        Args:
            activity_id: ID of the activity to delete.

        Returns:
            Confirmation message.
        """
        return client.delete(f"/activities/{activity_id}/delete")

    @mcp.tool()
    def get_activity_streams(activity_id: int) -> list[dict]:
        """
        Get GPS/sensor streams for an activity.

        Args:
            activity_id: ID of the activity.

        Returns:
            List of stream data points.
        """
        return client.get(f"/activities_streams/activity_id/{activity_id}/all") or []

    @mcp.tool()
    def get_activity_laps(activity_id: int) -> list[dict]:
        """
        Get lap data for an activity.

        Args:
            activity_id: ID of the activity.

        Returns:
            List of lap objects.
        """
        return client.get(f"/activities_laps/activity_id/{activity_id}/all") or []

    @mcp.tool()
    def refresh_activities() -> list[dict] | None:
        """
        Trigger a sync from connected integrations (Strava, Garmin Connect)
        for the last 24 hours and return newly fetched activities.

        Returns:
            List of activity objects or None.
        """
        return client.get("/activities/refresh")


def _me_id(client: EndurainClient) -> int:
    """Helper: return the authenticated user's ID via /profile."""
    me = client.get("/profile")
    return me["id"]
