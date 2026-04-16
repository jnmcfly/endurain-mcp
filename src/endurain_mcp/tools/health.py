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
        result = client.get(f"/health/sleep/page_number/{page_number}/num_records/{num_records}")
        if isinstance(result, dict):
            return result.get("records", [])
        return result or []

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
    def create_sleep(
        date: str,
        total_sleep_seconds: int,
        deep_sleep_seconds: int | None = None,
        light_sleep_seconds: int | None = None,
        rem_sleep_seconds: int | None = None,
        awake_seconds: int | None = None,
        sleep_start_time_gmt: str | None = None,
        sleep_end_time_gmt: str | None = None,
        sleep_score: int | None = None,
        avg_hrv_status: str | None = None,
    ) -> dict:
        """
        Create a new sleep record.

        Args:
            date: Date of the sleep record (YYYY-MM-DD).
            total_sleep_seconds: Total sleep duration in seconds.
            deep_sleep_seconds: Deep sleep in seconds.
            light_sleep_seconds: Light sleep in seconds.
            rem_sleep_seconds: REM sleep in seconds.
            awake_seconds: Awake seconds.
            sleep_start_time_gmt: Sleep start time (ISO-8601 datetime).
            sleep_end_time_gmt: Sleep end time (ISO-8601 datetime).
            sleep_score: Numeric sleep quality score.
            avg_hrv_status: HRV status string.

        Returns:
            Created HealthSleepRead object.
        """
        payload: dict = {"date": date, "total_sleep_seconds": total_sleep_seconds}
        for key, val in {
            "deep_sleep_seconds": deep_sleep_seconds,
            "light_sleep_seconds": light_sleep_seconds,
            "rem_sleep_seconds": rem_sleep_seconds,
            "awake_seconds": awake_seconds,
            "sleep_start_time_gmt": sleep_start_time_gmt,
            "sleep_end_time_gmt": sleep_end_time_gmt,
            "sleep_score": sleep_score,
            "avg_hrv_status": avg_hrv_status,
        }.items():
            if val is not None:
                payload[key] = val
        return client.post("/health/sleep", json=payload)

    @mcp.tool()
    def edit_sleep(sleep_id: int, **fields: object) -> dict:
        """
        Update a sleep record.

        Args:
            sleep_id: ID of the record to update.
            **fields: Any HealthSleepUpdate fields (total_sleep_seconds, deep_sleep_seconds, …).

        Returns:
            Updated HealthSleepRead object.
        """
        payload = {"id": sleep_id, **{k: v for k, v in fields.items() if v is not None}}
        return client.put("/health/sleep", json=payload)

    @mcp.tool()
    def delete_sleep(sleep_id: int) -> dict:
        """
        Delete a sleep record.

        Args:
            sleep_id: ID to delete.

        Returns:
            Confirmation message.
        """
        return client.delete(f"/health/sleep/{sleep_id}")

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
        result = client.get(f"/health/weight/page_number/{page_number}/num_records/{num_records}")
        if isinstance(result, dict):
            return result.get("records", [])
        return result or []

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
        date: str,
        weight: float,
        bmi: float | None = None,
        fat_percentage: float | None = None,
        muscle_mass_percentage: float | None = None,
        water_percentage: float | None = None,
        bone_mass: float | None = None,
    ) -> dict:
        """
        Log a weight measurement.

        Args:
            date: Date of measurement (YYYY-MM-DD).
            weight: Weight value in kg.
            bmi: Body Mass Index.
            fat_percentage: Body fat percentage.
            muscle_mass_percentage: Muscle mass percentage.
            water_percentage: Body water percentage.
            bone_mass: Bone mass in kg.

        Returns:
            Created HealthWeightRead object.
        """
        payload: dict = {"date": date, "weight": weight}
        for key, val in {
            "bmi": bmi,
            "fat_percentage": fat_percentage,
            "muscle_mass_percentage": muscle_mass_percentage,
            "water_percentage": water_percentage,
            "bone_mass": bone_mass,
        }.items():
            if val is not None:
                payload[key] = val
        return client.post("/health/weight", json=payload)

    @mcp.tool()
    def edit_weight(weight_id: int, **fields: object) -> dict:
        """
        Update a weight record.

        Args:
            weight_id: ID of the record to update.
            **fields: Any HealthWeightUpdate fields (weight, bmi, fat_percentage, …).

        Returns:
            Updated HealthWeightRead object.
        """
        payload = {"id": weight_id, **{k: v for k, v in fields.items() if v is not None}}
        return client.put("/health/weight", json=payload)

    @mcp.tool()
    def delete_weight(weight_id: int) -> dict:
        """
        Delete a weight record.

        Args:
            weight_id: ID to delete.

        Returns:
            Confirmation message.
        """
        return client.delete(f"/health/weight/{weight_id}")

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
        result = client.get(f"/health/steps/page_number/{page_number}/num_records/{num_records}")
        if isinstance(result, dict):
            return result.get("records", [])
        return result or []

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
    def create_steps(date: str, steps: int, calories: int | None = None) -> dict:
        """
        Log a daily step count.

        Args:
            date: Date (YYYY-MM-DD).
            steps: Number of steps.
            calories: Calories burned.

        Returns:
            Created HealthStepsRead object.
        """
        payload: dict = {"date": date, "steps": steps}
        if calories is not None:
            payload["calories"] = calories
        return client.post("/health/steps", json=payload)

    @mcp.tool()
    def edit_steps(steps_id: int, **fields: object) -> dict:
        """
        Update a steps record.

        Args:
            steps_id: ID of the record to update.
            **fields: Any HealthStepsUpdate fields (steps, calories, …).

        Returns:
            Updated HealthStepsRead object.
        """
        payload = {"id": steps_id, **{k: v for k, v in fields.items() if v is not None}}
        return client.put("/health/steps", json=payload)

    @mcp.tool()
    def delete_steps(steps_id: int) -> dict:
        """
        Delete a steps record.

        Args:
            steps_id: ID to delete.

        Returns:
            Confirmation message.
        """
        return client.delete(f"/health/steps/{steps_id}")

    # ------------------------------------------------------------------ Targets

    @mcp.tool()
    def get_health_targets() -> dict | None:
        """
        Get health targets for the authenticated user (steps, sleep, weight goals).

        Returns:
            Health targets object with weight, steps, sleep fields.
        """
        return client.get("/health_targets/")

    @mcp.tool()
    def edit_health_targets(**fields: object) -> dict:
        """
        Update health targets (e.g. daily steps goal, sleep goal).

        Args:
            **fields: Any HealthTargetsUpdate fields (steps, sleep_seconds, weight, …).

        Returns:
            Updated health targets object.
        """
        payload = {k: v for k, v in fields.items() if v is not None}
        return client.put("/health_targets/", json=payload)
