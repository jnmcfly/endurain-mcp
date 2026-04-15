"""Tests for health tools (sleep, weight, steps, targets)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from endurain_mcp.client import EndurainClient


@pytest.fixture()
def mock_client():
    return MagicMock(spec=EndurainClient)


class TestSleep:
    def test_list_sleep(self, mock_client):
        mock_client.get.return_value = [{"id": 1, "total_minutes": 480}]
        result = mock_client.get("/health/sleep/page_number/1/num_records/20") or []
        assert result[0]["total_minutes"] == 480

    def test_list_sleep_none_returns_empty(self, mock_client):
        mock_client.get.return_value = None
        result = mock_client.get("/health/sleep/page_number/1/num_records/20") or []
        assert result == []

    def test_create_sleep(self, mock_client):
        mock_client.post.return_value = {"id": 10, "sleep_date": "2026-04-15"}
        result = mock_client.post(
            "/health/sleep/create",
            json={"sleep_date": "2026-04-15", "total_minutes": 420},
        )
        assert result["id"] == 10

    def test_delete_sleep(self, mock_client):
        mock_client.delete.return_value = {"detail": "deleted"}
        mock_client.delete("/health/sleep/10/delete")
        mock_client.delete.assert_called_once_with("/health/sleep/10/delete")


class TestWeight:
    def test_list_weight(self, mock_client):
        mock_client.get.return_value = [{"id": 1, "weight": 75.0}]
        result = mock_client.get("/health/weight/page_number/1/num_records/20") or []
        assert result[0]["weight"] == 75.0

    def test_create_weight(self, mock_client):
        mock_client.post.return_value = {"id": 5, "weight": 74.5}
        result = mock_client.post(
            "/health/weight/create",
            json={"weight_date": "2026-04-15", "weight": 74.5},
        )
        assert result["weight"] == 74.5


class TestSteps:
    def test_list_steps(self, mock_client):
        mock_client.get.return_value = [{"id": 1, "steps": 10000}]
        result = mock_client.get("/health/steps/page_number/1/num_records/20") or []
        assert result[0]["steps"] == 10000

    def test_create_steps(self, mock_client):
        mock_client.post.return_value = {"id": 3, "steps": 8500}
        result = mock_client.post(
            "/health/steps/create",
            json={"steps_date": "2026-04-15", "steps": 8500},
        )
        assert result["steps"] == 8500


class TestHealthTargets:
    def test_list_targets(self, mock_client):
        mock_client.get.return_value = [{"id": 1, "target_type": "steps"}]
        result = mock_client.get("/health_targets") or []
        assert result[0]["target_type"] == "steps"

    def test_create_target(self, mock_client):
        mock_client.post.return_value = {"id": 2, "target_type": "weight"}
        result = mock_client.post(
            "/health_targets/create",
            json={"target_type": "weight", "target_value": 70.0},
        )
        assert result["target_type"] == "weight"

    def test_delete_target(self, mock_client):
        mock_client.delete.return_value = {"detail": "deleted"}
        mock_client.delete("/health_targets/2/delete")
        mock_client.delete.assert_called_once()
