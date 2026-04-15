"""MCP tools for Endurain health endpoints (sleep, weight, steps, targets)."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from endurain_mcp.client import EndurainClient


def register(mcp: FastMCP, client: EndurainClient) -> None:
    """Register all health-related MCP tools."""

    # ------------------------------------------------------------------ Sleep

    @mcp.tool()
    def list_sleep(page_number: int = 1, num_records: int = 20) -> list[dict]:
        """
        List sleep records for the authenticated user (paginated).

        Args:
            page_number: Page index starting at 1.
            num_records: Records per page.

        Returns:
            List of health sleep objects.
        """
        return (
            client.get(f"/health/sleep/page_number/{page_number}/num_records/{num_records}") or []
        )

    @mcp.tool()
    def get_sleep_count() -> int:
        """Return total count of sleep records for the authenticated user."""
        return client.get("/health/sleep/number")

    @mcp.tool()
    def get_sleep(sleep_id: int) -> dict:
        """
        Get a specific sleep record by ID.

        Args:
            sleep_id: Numeric sleep record ID.

        Returns:
            HealthSleepRead object.
        """
        return client.get(f"/health/sleep/{sleep_id}")

    @mcp.tool()
    def get_sleep_by_date(date: str) -> dict | None:
        """
        Get a sleep record for a specific date.

        Args:
            date: ISO-8601 date string (YYYY-MM-DD).

        Returns:
            HealthSleepRead object or None.
        """
        return client.get(f"/health/sleep/date/{date}")

    @mcp.tool()
    def create_sleep(
        sleep_date: str,
        total_minutes: int,
        deep_sleep_minutes: int | None = None,
        light_sleep_minutes: int | None = None,
        rem_sleep_minutes: int | None = None,
        awake_minutes: int | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        sleep_score: int | None = None,
        hrv_status: str | None = None,
    ) -> dict:
        """
        Create a new sleep record.

        Args:
            sleep_date: Date of the sleep record (YYYY-MM-DD).
            total_minutes: Total sleep duration in minutes.
            deep_sleep_minutes: Deep sleep in minutes.
            light_sleep_minutes: Light sleep in minutes.
            rem_sleep_minutes: REM sleep in minutes.
            awake_minutes: Awake minutes.
            start_time: Sleep start time (ISO-8601 datetime or time string).
            end_time: Sleep end time (ISO-8601 datetime or time string).
            sleep_score: Numeric sleep quality score.
            hrv_status: HRV status string.

        Returns:
            Created HealthSleepRead object.
        """
        payload: dict = {"sleep_date": sleep_date, "total_minutes": total_minutes}
        for key, val in {
            "deep_sleep_minutes": deep_sleep_minutes,
            "light_sleep_minutes": light_sleep_minutes,
            "rem_sleep_minutes": rem_sleep_minutes,
            "awake_minutes": awake_minutes,
            "start_time": start_time,
            "end_time": end_time,
            "sleep_score": sleep_score,
            "hrv_status": hrv_status,
        }.items():
            if val is not None:
                payload[key] = val
        return client.post("/health/sleep/create", json=payload)

    @mcp.tool()
    def edit_sleep(sleep_id: int, **fields: object) -> dict:
        """
        Update a sleep record.

        Args:
            sleep_id: ID of the record to update.
            **fields: Any HealthSleepUpdate fields (total_minutes, deep_sleep_minutes, …).

        Returns:
            Confirmation message.
        """
        payload = {"id": sleep_id, **{k: v for k, v in fields.items() if v is not None}}
        return client.put(f"/health/sleep/{sleep_id}/edit", json=payload)

    @mcp.tool()
    def delete_sleep(sleep_id: int) -> dict:
        """
        Delete a sleep record.

        Args:
            sleep_id: ID to delete.

        Returns:
            Confirmation message.
        """
        return client.delete(f"/health/sleep/{sleep_id}/delete")

    # ------------------------------------------------------------------ Weight

    @mcp.tool()
    def list_weight(page_number: int = 1, num_records: int = 20) -> list[dict]:
        """
        List weight records for the authenticated user (paginated).

        Args:
            page_number: Page index starting at 1.
            num_records: Records per page.

        Returns:
            List of health weight objects.
        """
        return (
            client.get(f"/health/weight/page_number/{page_number}/num_records/{num_records}") or []
        )

    @mcp.tool()
    def get_weight_count() -> int:
        """Return total count of weight records."""
        return client.get("/health/weight/number")

    @mcp.tool()
    def get_weight(weight_id: int) -> dict:
        """
        Get a weight record by ID.

        Args:
            weight_id: Numeric ID.

        Returns:
            HealthWeightRead object.
        """
        return client.get(f"/health/weight/{weight_id}")

    @mcp.tool()
    def create_weight(
        weight_date: str,
        weight: float,
        bmi: float | None = None,
        fat_percentage: float | None = None,
        muscle_percentage: float | None = None,
        water_percentage: float | None = None,
        bone_mass: float | None = None,
    ) -> dict:
        """
        Log a weight measurement.

        Args:
            weight_date: Date of measurement (YYYY-MM-DD).
            weight: Weight value in kg.
            bmi: Body Mass Index.
            fat_percentage: Body fat percentage.
            muscle_percentage: Muscle mass percentage.
            water_percentage: Body water percentage.
            bone_mass: Bone mass in kg.

        Returns:
            Created HealthWeightRead object.
        """
        payload: dict = {"weight_date": weight_date, "weight": weight}
        for key, val in {
            "bmi": bmi,
            "fat_percentage": fat_percentage,
            "muscle_percentage": muscle_percentage,
            "water_percentage": water_percentage,
            "bone_mass": bone_mass,
        }.items():
            if val is not None:
                payload[key] = val
        return client.post("/health/weight/create", json=payload)

    @mcp.tool()
    def delete_weight(weight_id: int) -> dict:
        """
        Delete a weight record.

        Args:
            weight_id: ID to delete.

        Returns:
            Confirmation message.
        """
        return client.delete(f"/health/weight/{weight_id}/delete")

    # ------------------------------------------------------------------ Steps

    @mcp.tool()
    def list_steps(page_number: int = 1, num_records: int = 20) -> list[dict]:
        """
        List daily step records (paginated).

        Args:
            page_number: Page index starting at 1.
            num_records: Records per page.

        Returns:
            List of health steps objects.
        """
        return (
            client.get(f"/health/steps/page_number/{page_number}/num_records/{num_records}") or []
        )

    @mcp.tool()
    def get_steps_count() -> int:
        """Return total count of step records."""
        return client.get("/health/steps/number")

    @mcp.tool()
    def get_steps(steps_id: int) -> dict:
        """
        Get a steps record by ID.

        Args:
            steps_id: Numeric ID.

        Returns:
            HealthStepsRead object.
        """
        return client.get(f"/health/steps/{steps_id}")

    @mcp.tool()
    def create_steps(steps_date: str, steps: int, calories: int | None = None) -> dict:
        """
        Log a daily step count.

        Args:
            steps_date: Date (YYYY-MM-DD).
            steps: Number of steps.
            calories: Calories burned.

        Returns:
            Created HealthStepsRead object.
        """
        payload: dict = {"steps_date": steps_date, "steps": steps}
        if calories is not None:
            payload["calories"] = calories
        return client.post("/health/steps/create", json=payload)

    @mcp.tool()
    def delete_steps(steps_id: int) -> dict:
        """
        Delete a steps record.

        Args:
            steps_id: ID to delete.

        Returns:
            Confirmation message.
        """
        return client.delete(f"/health/steps/{steps_id}/delete")

    # ------------------------------------------------------------------ Targets

    @mcp.tool()
    def list_health_targets() -> list[dict]:
        """
        List all health targets for the authenticated user.

        Returns:
            List of health target objects.
        """
        return client.get("/health_targets") or []

    @mcp.tool()
    def create_health_target(
        target_type: str,
        target_value: float,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict:
        """
        Create a health target (e.g. daily steps goal).

        Args:
            target_type: Type of target (e.g. "steps", "weight", "sleep").
            target_value: Numeric goal value.
            start_date: Optional start date (YYYY-MM-DD).
            end_date: Optional end date (YYYY-MM-DD).

        Returns:
            Created target object.
        """
        payload: dict = {"target_type": target_type, "target_value": target_value}
        if start_date:
            payload["start_date"] = start_date
        if end_date:
            payload["end_date"] = end_date
        return client.post("/health_targets/create", json=payload)

    @mcp.tool()
    def delete_health_target(target_id: int) -> dict:
        """
        Delete a health target.

        Args:
            target_id: ID to delete.

        Returns:
            Confirmation message.
        """
        return client.delete(f"/health_targets/{target_id}/delete")
