"""Endurain API HTTP client with automatic token management."""

from __future__ import annotations

import os
import time
import threading
from typing import Any

import httpx


API_PREFIX = "/api/v1"
CLIENT_TYPE = "mobile"


class AuthenticationError(Exception):
    """Raised when authentication against Endurain fails."""


class EndurainClient:
    """
    Thread-safe HTTP client for the Endurain REST API.

    Handles OAuth2 password-flow authentication for mobile clients,
    automatic token refresh on expiry, and progressive re-login on
    refresh-token expiry.

    Configuration is read from environment variables:
        ENDURAIN_BASE_URL  – Base URL of the Endurain instance (required)
        ENDURAIN_USERNAME  – Login username (required)
        ENDURAIN_PASSWORD  – Login password (required)
    """

    def __init__(
        self,
        base_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        self._base_url = (base_url or os.environ.get("ENDURAIN_BASE_URL", "")).rstrip("/")
        self._username = username or os.environ.get("ENDURAIN_USERNAME", "")
        self._password = password or os.environ.get("ENDURAIN_PASSWORD", "")

        if not self._base_url:
            raise ValueError("ENDURAIN_BASE_URL must be set")
        if not self._username:
            raise ValueError("ENDURAIN_USERNAME must be set")
        if not self._password:
            raise ValueError("ENDURAIN_PASSWORD must be set")

        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._expires_at: float = 0.0  # epoch seconds
        self._lock = threading.Lock()

        self._http = httpx.Client(
            base_url=self._base_url,
            timeout=30.0,
            headers={"X-Client-Type": CLIENT_TYPE},
        )

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def _login(self) -> None:
        """Perform username/password login and store tokens."""
        response = self._http.post(
            f"{API_PREFIX}/auth/login",
            data={"username": self._username, "password": self._password},
        )
        if response.status_code != 200:
            raise AuthenticationError(f"Login failed ({response.status_code}): {response.text}")
        data = response.json()
        self._store_tokens(data)

    def _refresh(self) -> bool:
        """
        Try to refresh the access token using the stored refresh token.

        Returns True on success, False when the refresh token has expired
        (caller should fall back to full re-login).
        """
        if not self._refresh_token:
            return False
        response = self._http.post(
            f"{API_PREFIX}/auth/refresh",
            headers={"Authorization": f"Bearer {self._refresh_token}"},
        )
        if response.status_code == 401:
            # Refresh token expired – need a new login
            return False
        if response.status_code != 200:
            raise AuthenticationError(
                f"Token refresh failed ({response.status_code}): {response.text}"
            )
        data = response.json()
        self._store_tokens(data)
        return True

    def _store_tokens(self, data: dict[str, Any]) -> None:
        self._access_token = data["access_token"]
        self._refresh_token = data.get("refresh_token")
        expires_in: int = data.get("expires_in", 900)
        # Subtract 30 s as a safety buffer
        self._expires_at = time.monotonic() + max(expires_in - 30, 0)

    def _ensure_authenticated(self) -> str:
        """Return a valid access token, refreshing or re-logging-in as needed."""
        with self._lock:
            now = time.monotonic()
            if self._access_token and now < self._expires_at:
                return self._access_token  # still valid

            # Try to refresh first (cheaper than full login)
            if self._refresh_token:
                if self._refresh():
                    return self._access_token  # type: ignore[return-value]

            # Fall back to full login
            self._login()
            return self._access_token  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # HTTP helpers
    # ------------------------------------------------------------------

    def _auth_headers(self) -> dict[str, str]:
        token = self._ensure_authenticated()
        return {"Authorization": f"Bearer {token}"}

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Execute a request, retrying once on 401 (token invalidated server-side)."""
        headers = self._auth_headers()
        headers.update(kwargs.pop("headers", {}))
        response = self._http.request(method, f"{API_PREFIX}{path}", headers=headers, **kwargs)

        if response.status_code == 401:
            # Force re-login and retry exactly once
            with self._lock:
                self._access_token = None
                self._expires_at = 0.0
            headers = self._auth_headers()
            response = self._http.request(method, f"{API_PREFIX}{path}", headers=headers, **kwargs)

        response.raise_for_status()
        # Some endpoints return 204 No Content or an empty body
        if response.status_code == 204 or not response.content.strip():
            return None
        try:
            return response.json()
        except Exception:
            return None

    def get(self, path: str, **kwargs: Any) -> Any:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Any:
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> Any:
        return self._request("PUT", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> Any:
        return self._request("DELETE", path, **kwargs)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "EndurainClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
