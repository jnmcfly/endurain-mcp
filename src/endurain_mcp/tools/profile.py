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
        goal_type: str,
        target_value: float,
        period: str,
        start_date: str | None = None,
        end_date: str | None = None,
        activity_type: int | None = None,
    ) -> dict:
        """
        Create a fitness goal.

        Args:
            goal_type: Type string (e.g. "distance", "duration", "elevation").
            target_value: Numeric target.
            period: Period string (e.g. "week", "month", "year").
            start_date: Optional start date (YYYY-MM-DD).
            end_date: Optional end date (YYYY-MM-DD).
            activity_type: Limit to a specific activity type.

        Returns:
            Created goal object.
        """
        payload: dict = {
            "goal_type": goal_type,
            "target_value": target_value,
            "period": period,
        }
        for key, val in {
            "start_date": start_date,
            "end_date": end_date,
            "activity_type": activity_type,
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
            Default-gear object mapping activity types to gear IDs.
        """
        return client.get("/profile/default_gear")

    @mcp.tool()
    def set_default_gear(activity_type: int, gear_id: int) -> dict:
        """
        Assign a default gear for an activity type.

        Args:
            activity_type: Numeric activity type.
            gear_id: Gear ID to assign.

        Returns:
            Updated default-gear object.
        """
        return client.put(
            "/profile/default_gear",
            json={"activity_type": activity_type, "gear_id": gear_id},
        )

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
    def edit_server_settings(**fields: object) -> dict:
        """
        Update server settings (admin only).

        Args:
            **fields: Any server settings fields to update.

        Returns:
            Updated server settings object.
        """
        payload = {k: v for k, v in fields.items() if v is not None}
        return client.put("/server_settings", json=payload)
