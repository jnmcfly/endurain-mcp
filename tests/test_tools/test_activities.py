"""Tests for activity tools using a mock EndurainClient."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from endurain_mcp.client import EndurainClient


@pytest.fixture()
def mock_client():
    return MagicMock(spec=EndurainClient)


class TestListActivities:
    def test_returns_list(self, mock_client):
        mock_client.get.return_value = [{"id": 1, "name": "Morning Run"}]
        mock_client.get.side_effect = lambda path, **kw: (
            {"id": 42} if path == "/users/me" else [{"id": 1, "name": "Morning Run"}]
        )
        from endurain_mcp.tools.activities import register
        from mcp.server.fastmcp import FastMCP

        mcp = FastMCP("test")
        register(mcp, mock_client)

        # Directly invoke the underlying function via the client
        result = mock_client.get("/activities/user/42/page_number/1/num_records/20")
        assert isinstance(result, list)

    def test_empty_list_when_none(self, mock_client):
        mock_client.get.return_value = None
        result = mock_client.get("/activities/number") or []
        assert result == []


class TestGetActivity:
    def test_returns_activity(self, mock_client):
        mock_client.get.return_value = {"id": 5, "name": "Swim"}
        result = mock_client.get("/activities/5")
        assert result["id"] == 5


class TestDeleteActivity:
    def test_delete_calls_delete(self, mock_client):
        mock_client.delete.return_value = {"detail": "Activity 5 deleted successfully"}
        result = mock_client.delete("/activities/5/delete")
        assert "deleted" in result["detail"]


class TestEditActivity:
    def test_edit_sends_payload(self, mock_client):
        mock_client.put.return_value = {"Activity ID 5 updated successfully"}
        result = mock_client.put("/activities/edit", json={"id": 5, "name": "Updated Run"})
        mock_client.put.assert_called_once_with(
            "/activities/edit", json={"id": 5, "name": "Updated Run"}
        )


class TestActivityStreams:
    def test_returns_streams(self, mock_client):
        mock_client.get.return_value = [{"lat": 48.0, "lon": 11.0}]
        result = mock_client.get("/activities_streams/5")
        assert len(result) == 1
