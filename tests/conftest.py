"""Shared fixtures for the endurain-mcp test suite."""

from __future__ import annotations

import pytest

from endurain_mcp.client import EndurainClient

BASE_URL = "http://endurain.test"
LOGIN_RESPONSE = {
    "access_token": "test-access-token",
    "refresh_token": "test-refresh-token",
    "token_type": "bearer",
    "expires_in": 900,
    "refresh_token_expires_in": 604800,
}


@pytest.fixture()
def mock_transport(httpx_mock):
    """
    Pre-configure httpx_mock with a successful login response so that
    EndurainClient.__init__ → _ensure_authenticated works out of the box.
    """
    httpx_mock.add_response(
        method="POST",
        url=f"{BASE_URL}/api/v1/auth/login",
        json=LOGIN_RESPONSE,
        status_code=200,
    )
    return httpx_mock


@pytest.fixture()
def client(mock_transport) -> EndurainClient:
    """Return an EndurainClient wired to the mock transport."""
    return EndurainClient(
        base_url=BASE_URL,
        username="admin",
        password="admin",
    )
