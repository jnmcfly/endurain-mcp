"""Tests for user, session, and follower tools."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from endurain_mcp.client import EndurainClient


@pytest.fixture()
def mock_client():
    return MagicMock(spec=EndurainClient)


class TestUsers:
    def test_get_me(self, mock_client):
        mock_client.get.return_value = {"id": 1, "username": "admin"}
        result = mock_client.get("/users/me")
        assert result["username"] == "admin"

    def test_list_users(self, mock_client):
        mock_client.get.return_value = [{"id": 1}, {"id": 2}]
        result = mock_client.get("/users/page_number/1/num_records/20") or []
        assert len(result) == 2

    def test_get_user(self, mock_client):
        mock_client.get.return_value = {"id": 2, "username": "alice"}
        result = mock_client.get("/users/2")
        assert result["username"] == "alice"

    def test_create_user(self, mock_client):
        mock_client.post.return_value = {"id": 3, "username": "bob"}
        result = mock_client.post(
            "/users/create",
            json={"username": "bob", "email": "bob@x.com", "password": "s3cr3t"},
        )
        assert result["username"] == "bob"

    def test_delete_user(self, mock_client):
        mock_client.delete.return_value = {"detail": "User 3 deleted"}
        result = mock_client.delete("/users/3/delete")
        assert "deleted" in result["detail"]


class TestSessions:
    def test_list_sessions(self, mock_client):
        mock_client.get.return_value = [{"id": "abc-123"}]
        result = mock_client.get("/sessions") or []
        assert result[0]["id"] == "abc-123"

    def test_delete_session(self, mock_client):
        mock_client.delete.return_value = {"detail": "Session deleted"}
        mock_client.delete("/sessions/abc-123/delete")
        mock_client.delete.assert_called_once_with("/sessions/abc-123/delete")


class TestFollowers:
    def test_list_followers(self, mock_client):
        mock_client.get.return_value = [{"follower_id": 2}]
        result = mock_client.get("/followers/1") or []
        assert result[0]["follower_id"] == 2

    def test_follow_user(self, mock_client):
        mock_client.post.return_value = {"detail": "Now following"}
        result = mock_client.post("/followers/2/add")
        assert result is not None

    def test_unfollow_user(self, mock_client):
        mock_client.delete.return_value = {"detail": "Unfollowed"}
        mock_client.delete("/followers/2/delete")
        mock_client.delete.assert_called_once_with("/followers/2/delete")
