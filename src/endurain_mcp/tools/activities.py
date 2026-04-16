"""MCP tools for Endurain activity endpoints."""

from __future__ import annotations

from datetime import date

from mcp.server.fastmcp import FastMCP

from endurain_mcp.client import EndurainClient
from endurain_mcp.tools.utils import me_id as _me_id


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
            sort_by: Field to sort by. Allowed values: "start_time", "distance",
                "duration", "pace", "elevation", "calories", "average_hr",
                "name", "type", "location". Default order is by start_time desc.
            sort_order: "asc" or "desc".

        Returns:
            List of activity objects.
        """
        _VALID_SORT_BY = {
            "start_time",
            "distance",
            "duration",
            "pace",
            "elevation",
            "calories",
            "average_hr",
            "name",
            "type",
            "location",
        }
        if sort_by and sort_by not in _VALID_SORT_BY:
            raise ValueError(
                f"Invalid sort_by '{sort_by}'. Allowed: {', '.join(sorted(_VALID_SORT_BY))}"
            )
        if sort_order and sort_order not in {"asc", "desc"}:
            raise ValueError(f"Invalid sort_order '{sort_order}'. Allowed: 'asc', 'desc'")

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
        Edit an existing activity. Only the fields you supply will be changed.

        Args:
            activity_id: ID of the activity to edit.
            name: New name.
            description: New description.
            visibility: Visibility level (0=private, 1=followers, 2=public).
            gear_id: Associated gear ID (use null to remove gear).

        Returns:
            Updated activity object.
        """
        # Fetch current values to satisfy required fields (name, activity_type)
        current = client.get(f"/activities/{activity_id}")
        payload: dict = {
            "id": activity_id,
            "name": current.get("name"),
            "activity_type": current.get("activity_type"),
        }
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
    def get_distance_stats(
        start_date: str,
        end_date: str | None = None,
        activity_type: int | None = None,
        user_id: int | None = None,
    ) -> dict:
        """
        Aggregate total distance and activity count for a date range.
        Use this for questions like "how many km did I run this year/month/week?".

        Distance values in the response are in kilometers (km).

        Activity type codes (most common):
          1 = Run, 2 = Trail Run, 3 = Virtual Run,
          4 = Ride (Bike), 5 = Gravel Ride, 6 = Mountain Bike, 7 = Virtual Ride,
          8 = Open Water Swim, 9 = Walk, 10 = Hike

        Args:
            start_date: Start of period (YYYY-MM-DD), e.g. "2026-01-01" for year-to-date.
            end_date: End of period (YYYY-MM-DD), defaults to today.
            activity_type: Filter to a specific activity type (see codes above).
            user_id: User ID (defaults to authenticated user).

        Returns:
            Dict with total_distance_km, total_count, and per_type breakdown.
        """
        uid = user_id or _me_id(client)
        end = end_date or date.today().isoformat()

        params: dict = {"start_date": start_date, "end_date": end}
        if activity_type is not None:
            params["type"] = activity_type

        # Fetch all pages
        all_activities: list[dict] = []
        page = 1
        page_size = 100
        while True:
            batch = client.get(
                f"/activities/user/{uid}/page_number/{page}/num_records/{page_size}",
                params=params,
            )
            if not batch:
                break
            all_activities.extend(batch)
            if len(batch) < page_size:
                break
            page += 1

        # Aggregate
        total_meters = sum(a.get("distance", 0) or 0 for a in all_activities)
        by_type: dict[int, dict] = {}
        for a in all_activities:
            t = a.get("activity_type", 0)
            if t not in by_type:
                by_type[t] = {"count": 0, "distance_km": 0.0}
            by_type[t]["count"] += 1
            by_type[t]["distance_km"] = round(
                by_type[t]["distance_km"] + (a.get("distance", 0) or 0) / 1000, 2
            )

        return {
            "start_date": start_date,
            "end_date": end,
            "total_distance_km": round(total_meters / 1000, 2),
            "total_count": len(all_activities),
            "per_type": by_type,
        }

    @mcp.tool()
    def refresh_activities() -> list[dict] | None:
        """
        Trigger a sync from connected integrations (Strava, Garmin Connect)
        for the last 24 hours and return newly fetched activities.

        Returns:
            List of activity objects or None.
        """
        return client.get("/activities/refresh")
