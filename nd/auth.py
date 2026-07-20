"""Authentication for ND: obtain and cache a JWT from POST /api/v1/infra/login.

The token is reused across the Manage/Analyze/OneManage services via the
`Authorization: Bearer` header (ND also accepts an `AuthCookie` cookie).
"""

from __future__ import annotations

import httpx

from .config import NdConfig
from .errors import NdAuthError


class Authenticator:
    """Manages the ND session token lifecycle for a shared httpx client."""

    def __init__(self, config: NdConfig, http: httpx.Client) -> None:
        self._config = config
        self._http = http
        self._token: str | None = None

    @property
    def token(self) -> str:
        """Return a valid token, logging in on first use."""
        if self._token is None:
            self.login()
        assert self._token is not None
        return self._token

    def auth_headers(self) -> dict[str, str]:
        """Headers to attach to authenticated requests."""
        return {"Authorization": f"Bearer {self.token}"}

    def invalidate(self) -> None:
        """Drop the cached token so the next request re-authenticates."""
        self._token = None

    def login(self) -> None:
        """Authenticate against ND and cache the JWT.

        Raises:
            NdAuthError: on network failure, non-200 status, or a missing token.
        """
        payload = {
            "userName": self._config.username,
            "userPasswd": self._config.password,
            "domain": self._config.domain,
        }
        try:
            resp = self._http.post(self._config.login_path, json=payload)
        except httpx.HTTPError as exc:
            raise NdAuthError(f"Could not reach ND login endpoint: {exc}") from exc

        if resp.status_code != 200:
            # Never echo the request body (contains the password).
            detail = _safe_message(resp)
            raise NdAuthError(
                f"ND login failed (HTTP {resp.status_code}) for user "
                f"{self._config.username!r} in domain {self._config.domain!r}: {detail}"
            )

        try:
            data = resp.json()
        except ValueError as exc:
            raise NdAuthError("ND login response was not valid JSON.") from exc

        token = data.get("jwttoken") or data.get("token")
        if not token:
            raise NdAuthError("ND login succeeded but no 'jwttoken' was returned.")
        self._token = token


def _safe_message(resp: httpx.Response) -> str:
    """Extract a short error message without leaking sensitive content."""
    try:
        body = resp.json()
    except ValueError:
        return resp.text[:200]
    if isinstance(body, dict):
        return str(body.get("message") or body.get("error") or body)[:200]
    return str(body)[:200]
