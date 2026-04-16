"""MCP tools for Endurain gear endpoints."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from endurain_mcp.client import EndurainClient


def register(mcp: FastMCP, client: EndurainClient) -> None:
    """Register all gear-related MCP tools."""

    @mcp.tool()
    def list_gears(page_number: int = 1, num_records: int = 20) -> list[dict]:
        """
        List gear items for the authenticated user (paginated).

        Args:
            page_number: Page index starting at 1.
            num_records: Records per page.

        Returns:
            List of gear objects (bikes, shoes, wetsuits, etc.).
        """
        result = client.get(f"/gears/page_number/{page_number}/num_records/{num_records}")
        if isinstance(result, dict):
            return result.get("records", [])
        return result or []

    @mcp.tool()
    def get_gear(gear_id: int) -> dict:
        """
        Get a specific gear item by ID.

        Args:
            gear_id: Numeric gear ID.

        Returns:
            Gear object.
        """
        return client.get(f"/gears/id/{gear_id}")

    @mcp.tool()
    def create_gear(
        gear_type: int,
        brand: str | None = None,
        model: str | None = None,
        nickname: str | None = None,
        initial_kms: float | None = None,
    ) -> dict:
        """
        Create a new gear item.

        Args:
            gear_type: Numeric type (e.g. 1=bike, 2=shoes, 3=wetsuit, …).
            brand: Brand name.
            model: Model name.
            nickname: Short nickname.
            initial_kms: Pre-existing kilometres at registration.

        Returns:
            Created gear object.
        """
        payload: dict = {"gear_type": gear_type}
        for key, val in {
            "brand": brand,
            "model": model,
            "nickname": nickname,
            "initial_kms": initial_kms,
        }.items():
            if val is not None:
                payload[key] = val
        return client.post("/gears", json=payload)

    @mcp.tool()
    def edit_gear(
        gear_id: int,
        brand: str | None = None,
        model: str | None = None,
        nickname: str | None = None,
        is_active: bool | None = None,
    ) -> dict:
        """
        Edit a gear item.

        Args:
            gear_id: ID of the gear to edit.
            brand: New brand.
            model: New model.
            nickname: New nickname.
            is_active: Active status.

        Returns:
            Updated gear object.
        """
        payload: dict = {"id": gear_id}
        for key, val in {
            "brand": brand,
            "model": model,
            "nickname": nickname,
            "is_active": is_active,
        }.items():
            if val is not None:
                payload[key] = val
        return client.put(f"/gears/{gear_id}", json=payload)

    @mcp.tool()
    def delete_gear(gear_id: int) -> dict:
        """
        Delete a gear item.

        Args:
            gear_id: ID to delete.

        Returns:
            Confirmation message.
        """
        return client.delete(f"/gears/{gear_id}")

    @mcp.tool()
    def list_gear_components(gear_id: int) -> list[dict]:
        """
        List components attached to a gear item.

        Args:
            gear_id: Parent gear ID.

        Returns:
            List of gear component objects.
        """
        return client.get(f"/gear_components/gear_id/{gear_id}") or []

    @mcp.tool()
    def create_gear_component(
        gear_id: int,
        component_type: str,
        brand: str | None = None,
        model: str | None = None,
        initial_kms: float | None = None,
    ) -> dict:
        """
        Add a component to a gear item.

        Args:
            gear_id: Parent gear ID.
            component_type: Type label (e.g. "chain", "tyre").
            brand: Brand name.
            model: Model name.
            initial_kms: Pre-existing kilometres.

        Returns:
            Created gear component object.
        """
        payload: dict = {"gear_id": gear_id, "component_type": component_type}
        for key, val in {
            "brand": brand,
            "model": model,
            "initial_kms": initial_kms,
        }.items():
            if val is not None:
                payload[key] = val
        return client.post("/gear_components", json=payload)

    @mcp.tool()
    def delete_gear_component(component_id: int) -> dict:
        """
        Delete a gear component.

        Args:
            component_id: ID to delete.

        Returns:
            Confirmation message.
        """
        return client.delete(f"/gear_components/{component_id}")

    @mcp.tool()
    def get_activities_by_gear(
        gear_id: int, page_number: int = 1, num_records: int = 20
    ) -> list[dict]:
        """
        List all activities that used a specific gear item (paginated).

        Args:
            gear_id: Gear ID.
            page_number: Page index starting at 1.
            num_records: Records per page.

        Returns:
            List of activity objects.
        """
        return (
            client.get(
                f"/activities/gear/{gear_id}/page_number/{page_number}/num_records/{num_records}"
            )
            or []
        )
