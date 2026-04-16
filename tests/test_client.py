"""Unit tests for EnduRainClient authentication and HTTP helpers."""

from __future__ import annotations

import pytest

from endurain_mcp.client import API_PREFIX, AuthenticationError, EndurainClient

BASE_URL = "http://endurain.test"
LOGIN_URL = f"{BASE_URL}{API_PREFIX}/auth/login"
REFRESH_URL = f"{BASE_URL}{API_PREFIX}/auth/refresh"


LOGIN_PAYLOAD = {
    "access_token": "acc",
    "refresh_token": "ref",
    "token_type": "bearer",
    "expires_in": 900,
    "refresh_token_expires_in": 604800,
}


def test_client_requires_base_url(monkeypatch):
    monkeypatch.delenv("ENDURAIN_BASE_URL", raising=False)
    with pytest.raises(ValueError, match="ENDURAIN_BASE_URL"):
        EndurainClient(username="u", password="p")


def test_client_requires_username(monkeypatch):
    monkeypatch.delenv("ENDURAIN_USERNAME", raising=False)
    with pytest.raises(ValueError, match="ENDURAIN_USERNAME"):
        EndurainClient(base_url=BASE_URL, password="p")


def test_client_requires_password(monkeypatch):
    monkeypatch.delenv("ENDURAIN_PASSWORD", raising=False)
    with pytest.raises(ValueError, match="ENDURAIN_PASSWORD"):
        EndurainClient(base_url=BASE_URL, username="u")


def test_login_success(httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url=LOGIN_URL,
        json=LOGIN_PAYLOAD,
        status_code=200,
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE_URL}{API_PREFIX}/users/me",
        json={"id": 1, "username": "admin"},
        status_code=200,
    )

    c = EndurainClient(base_url=BASE_URL, username="admin", password="admin")
    result = c.get("/users/me")
    assert result["id"] == 1
    assert c._access_token == "acc"


def test_login_failure_raises(httpx_mock):
    httpx_mock.add_response(
        method="POST",
        url=LOGIN_URL,
        json={"detail": "Incorrect username or password"},
        status_code=401,
    )
    with pytest.raises(AuthenticationError, match="Login failed"):
        EndurainClient(base_url=BASE_URL, username="bad", password="wrong")._login()


def test_token_refresh_on_expiry(httpx_mock):
    """Client re-uses refresh token when access token expires."""
    # First call triggers initial login
    httpx_mock.add_response(method="POST", url=LOGIN_URL, json=LOGIN_PAYLOAD)
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE_URL}{API_PREFIX}/ping",
        json={"ok": True},
    )
    # Second call: expired token → refresh
    httpx_mock.add_response(
        method="POST",
        url=REFRESH_URL,
        json={**LOGIN_PAYLOAD, "access_token": "new-acc"},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE_URL}{API_PREFIX}/ping",
        json={"ok": True},
    )

    c = EndurainClient(base_url=BASE_URL, username="u", password="p")
    c.get("/ping")  # triggers initial lazy login
    c._expires_at = 0.0  # expire the access token
    c.get("/ping")  # should use refresh token, not re-login
    assert c._access_token == "new-acc"


def test_relogin_when_refresh_fails(httpx_mock):
    """Client falls back to full login when refresh token is rejected."""
    # First call triggers initial lazy login
    httpx_mock.add_response(method="POST", url=LOGIN_URL, json=LOGIN_PAYLOAD)
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE_URL}{API_PREFIX}/ping",
        json={"ok": True},
    )
    # Second call: expired → refresh rejected → full re-login
    httpx_mock.add_response(method="POST", url=REFRESH_URL, status_code=401)
    httpx_mock.add_response(
        method="POST",
        url=LOGIN_URL,
        json={**LOGIN_PAYLOAD, "access_token": "fresh-acc"},
    )
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE_URL}{API_PREFIX}/ping",
        json={"ok": True},
    )

    c = EndurainClient(base_url=BASE_URL, username="u", password="p")
    c.get("/ping")  # triggers initial lazy login
    c._expires_at = 0.0  # expire the token
    c.get("/ping")  # refresh fails → full re-login
    assert c._access_token == "fresh-acc"


def test_retry_on_401(httpx_mock):
    """Client retries with a fresh token after receiving a 401 on a normal request."""
    httpx_mock.add_response(method="POST", url=LOGIN_URL, json=LOGIN_PAYLOAD)
    # First request: 401
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE_URL}{API_PREFIX}/protected",
        status_code=401,
    )
    # Refresh
    httpx_mock.add_response(
        method="POST",
        url=REFRESH_URL,
        json={**LOGIN_PAYLOAD, "access_token": "retry-acc"},
    )
    # Retry succeeds
    httpx_mock.add_response(
        method="GET",
        url=f"{BASE_URL}{API_PREFIX}/protected",
        json={"data": "ok"},
    )

    c = EndurainClient(base_url=BASE_URL, username="u", password="p")
    result = c.get("/protected")
    assert result == {"data": "ok"}


@pytest.mark.httpx_mock(assert_all_responses_were_requested=False)
def test_context_manager_closes_client(httpx_mock):
    httpx_mock.add_response(method="POST", url=LOGIN_URL, json=LOGIN_PAYLOAD)
    with EndurainClient(base_url=BASE_URL, username="u", password="p") as c:
        pass  # no requests made – just verify the context manager closes the transport
    assert c._http.is_closed
