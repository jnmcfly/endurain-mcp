"""MCP tools for Endurain profile, goals, notifications, and server settings."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from endurain_mcp.client import EndurainClient


def register(mcp: FastMCP, client: EndurainClient) -> None:
    """Register profile, goals, notifications, and server-settings tools."""

    # ----------------------------------------------------------------- Goals

    @mcp.tool()
    def list_goals() -> list[dict]:
        """
        List all fitness goals for the authenticated user.

        Returns:
            List of goal objects.
        """
        return client.get("/profile/goals") or []

    @mcp.tool()
    def create_goal(
        interval: str,
        activity_type: str,
        goal_type: str,
        goal_distance: int | None = None,
        goal_duration: int | None = None,
        goal_elevation: int | None = None,
        goal_calories: int | None = None,
        goal_activities_number: int | None = None,
    ) -> dict:
        """
        Create a fitness goal.

        interval values: "daily", "weekly", "monthly", "yearly"
        activity_type values: "run", "bike", "swim", "walk", "strength", "cardio"
        goal_type values: "distance", "duration", "elevation", "calories", "activities"

        Set exactly one goal value matching the goal_type:
          - goal_type="distance"   → goal_distance in meters (e.g. 100000 = 100 km)
          - goal_type="duration"   → goal_duration in seconds
          - goal_type="elevation"  → goal_elevation in meters
          - goal_type="calories"   → goal_calories in kcal
          - goal_type="activities" → goal_activities_number (count)

        Args:
            interval: Recurrence interval ("daily", "weekly", "monthly", "yearly").
            activity_type: Activity type ("run", "bike", "swim", "walk", "strength", "cardio").
            goal_type: Metric to track ("distance", "duration", "elevation", "calories", "activities").
            goal_distance: Target distance in meters.
            goal_duration: Target duration in seconds.
            goal_elevation: Target elevation gain in meters.
            goal_calories: Target calories in kcal.
            goal_activities_number: Target number of activities.

        Returns:
            Created goal object.
        """
        payload: dict = {
            "interval": interval,
            "activity_type": activity_type,
            "goal_type": goal_type,
        }
        for key, val in {
            "goal_distance": goal_distance,
            "goal_duration": goal_duration,
            "goal_elevation": goal_elevation,
            "goal_calories": goal_calories,
            "goal_activities_number": goal_activities_number,
        }.items():
            if val is not None:
                payload[key] = val
        return client.post("/profile/goals", json=payload)

    @mcp.tool()
    def delete_goal(goal_id: int) -> dict:
        """
        Delete a fitness goal.

        Args:
            goal_id: ID to delete.

        Returns:
            Confirmation message.
        """
        return client.delete(f"/profile/goals/{goal_id}")

    # --------------------------------------------------------- Default gear

    @mcp.tool()
    def get_default_gear() -> dict | None:
        """
        Get default gear assignments per activity type.

        Returns:
            Default-gear object mapping activity types to gear IDs
            (run_gear_id, ride_gear_id, walk_gear_id, etc.).
        """
        return client.get("/profile/default_gear")

    @mcp.tool()
    def set_default_gear(activity_type_field: str, gear_id: int | None) -> dict:
        """
        Set or clear a default gear for an activity type.

        activity_type_field must be one of:
          run_gear_id, trail_run_gear_id, virtual_run_gear_id,
          ride_gear_id, gravel_ride_gear_id, mtb_ride_gear_id, virtual_ride_gear_id,
          ows_gear_id, walk_gear_id, hike_gear_id, tennis_gear_id,
          alpine_ski_gear_id, nordic_ski_gear_id, snowboard_gear_id, windsurf_gear_id

        Args:
            activity_type_field: The field name to set (e.g. "run_gear_id").
            gear_id: Gear ID to assign, or null to clear.

        Returns:
            Updated default-gear object.
        """
        # Fetch current to merge (all fields required by API)
        current = client.get("/profile/default_gear")
        me = client.get("/profile")
        payload = {**current, "user_id": me["id"], activity_type_field: gear_id}
        return client.put("/profile/default_gear", json=payload)

    # --------------------------------------------------------- Notifications

    @mcp.tool()
    def list_notifications(page_number: int = 1, num_records: int = 50) -> list[dict]:
        """
        List notifications for the authenticated user (paginated).

        Args:
            page_number: Page index starting at 1.
            num_records: Records per page.

        Returns:
            List of notification objects.
        """
        return (
            client.get(f"/notifications/page_number/{page_number}/num_records/{num_records}") or []
        )

    @mcp.tool()
    def mark_notification_read(notification_id: int) -> dict:
        """
        Mark a specific notification as read.

        Args:
            notification_id: ID of the notification to mark as read.

        Returns:
            Confirmation message.
        """
        return client.put(f"/notifications/{notification_id}/mark_as_read")

    # --------------------------------------------------------- Server settings

    @mcp.tool()
    def get_server_settings() -> dict:
        """
        Get current server settings (admin only).

        Returns:
            Server settings object.
        """
        return client.get("/server_settings")

    @mcp.tool()
    def edit_server_settings(
        units: str | None = None,
        num_records_per_page: int | None = None,
        public_shareable_links: bool | None = None,
        public_shareable_links_user_info: bool | None = None,
        signup_enabled: bool | None = None,
        signup_require_admin_approval: bool | None = None,
        signup_require_email_verification: bool | None = None,
        sso_enabled: bool | None = None,
        local_login_enabled: bool | None = None,
        sso_auto_redirect: bool | None = None,
        tileserver_url: str | None = None,
        tileserver_attribution: str | None = None,
        map_background_color: str | None = None,
        currency: str | None = None,
    ) -> dict:
        """
        Update server settings (admin only). Only supply the fields you want to change.

        Args:
            units: Default units ("metric" or "imperial").
            num_records_per_page: Default page size.
            public_shareable_links: Allow public shareable links.
            public_shareable_links_user_info: Include user info in shareable links.
            signup_enabled: Allow new registrations.
            signup_require_admin_approval: Require admin approval for new accounts.
            signup_require_email_verification: Require email verification.
            sso_enabled: Enable SSO login.
            local_login_enabled: Enable local username/password login.
            sso_auto_redirect: Auto-redirect to SSO provider.
            tileserver_url: Custom map tile server URL.
            tileserver_attribution: Map tile server attribution text.
            map_background_color: Map background color hex code.
            currency: Default currency code.

        Returns:
            Updated server settings object.
        """
        # Fetch current to fill all required fields
        current = client.get("/server_settings")
        updates = {
            k: v
            for k, v in {
                "units": units,
                "num_records_per_page": num_records_per_page,
                "public_shareable_links": public_shareable_links,
                "public_shareable_links_user_info": public_shareable_links_user_info,
                "signup_enabled": signup_enabled,
                "signup_require_admin_approval": signup_require_admin_approval,
                "signup_require_email_verification": signup_require_email_verification,
                "sso_enabled": sso_enabled,
                "local_login_enabled": local_login_enabled,
                "sso_auto_redirect": sso_auto_redirect,
                "tileserver_url": tileserver_url,
                "tileserver_attribution": tileserver_attribution,
                "map_background_color": map_background_color,
                "currency": currency,
            }.items()
            if v is not None
        }
        payload = {**current, **updates}
        return client.put("/server_settings", json=payload)
