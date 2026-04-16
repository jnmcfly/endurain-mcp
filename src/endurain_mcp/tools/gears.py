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
        nickname: str,
        gear_type: int,
        brand: str | None = None,
        model: str | None = None,
        initial_kms: float | None = None,
        purchase_value: float | None = None,
    ) -> dict:
        """
        Create a new gear item.

        Gear type codes:
          1 = Bike, 2 = Shoes, 3 = Wetsuit, 4 = Ski, 5 = Snowboard,
          6 = Kayak, 7 = Surfboard, 8 = Other

        Args:
            nickname: Short display name for the gear (required, must be unique).
            gear_type: Numeric type code (see above).
            brand: Brand name.
            model: Model name.
            initial_kms: Pre-existing kilometres at registration.
            purchase_value: Purchase price.

        Returns:
            Created gear object.
        """
        payload: dict = {
            "nickname": nickname,
            "gear_type": gear_type,
            "active": True,
            "initial_kms": initial_kms if initial_kms is not None else 0,
        }
        for key, val in {
            "brand": brand,
            "model": model,
            "purchase_value": purchase_value,
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
        active: bool | None = None,
        initial_kms: float | None = None,
        purchase_value: float | None = None,
    ) -> dict:
        """
        Edit a gear item. Only the fields you supply will be changed.

        Args:
            gear_id: ID of the gear to edit.
            brand: New brand.
            model: New model.
            nickname: New nickname.
            active: Active status.
            initial_kms: Pre-existing kilometres.
            purchase_value: Purchase price.

        Returns:
            Updated gear object.
        """
        # Fetch current values to satisfy required fields (nickname, gear_type)
        current = client.get(f"/gears/id/{gear_id}")
        payload: dict = {
            "id": gear_id,
            "nickname": current.get("nickname"),
            "gear_type": current.get("gear_type"),
        }
        for key, val in {
            "brand": brand,
            "model": model,
            "nickname": nickname,
            "active": active,
            "initial_kms": initial_kms,
            "purchase_value": purchase_value,
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
        type: str,
        brand: str,
        model: str,
        purchase_date: str,
        retired_date: str | None = None,
    ) -> dict:
        """
        Add a component to a gear item.

        Args:
            gear_id: Parent gear ID.
            type: Component type label (e.g. "chain", "tyre", "brake_pad").
            brand: Brand name (required).
            model: Model name (required).
            purchase_date: Purchase date (YYYY-MM-DD, required).
            retired_date: Retirement date (YYYY-MM-DD).

        Returns:
            Created gear component object.
        """
        me = client.get("/profile")
        payload: dict = {
            "gear_id": gear_id,
            "user_id": me["id"],
            "type": type,
            "brand": brand,
            "model": model,
            "purchase_date": purchase_date,
        }
        if retired_date is not None:
            payload["retired_date"] = retired_date
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
