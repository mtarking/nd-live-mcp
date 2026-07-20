"""HTTP core for the ND live client — read-only (GET) access with auth + retry.

This is the reusable library layer. It is consumed three ways:
- by the MCP server (`server.py`) for AgenticOps / interactive use,
- by `tests/` directly (deterministic, no LLM),
- by any pipeline / Ansible validate role that imports `nd`.
"""

from __future__ import annotations

from typing import Any

import httpx

from .auth import Authenticator
from .config import NdConfig
from .errors import NdApiError, NdError


class NdClient:
    """A read-only client for a single ND cluster.

    Only HTTP GET is exposed by design (v1 is read-only). A `transport` may be
    injected for deterministic testing without a live ND.
    """

    def __init__(
        self,
        config: NdConfig,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._config = config
        self._http = httpx.Client(
            base_url=config.host,
            verify=config.verify_tls,
            timeout=config.timeout,
            transport=transport,
        )
        self._auth = Authenticator(config, self._http)

    # -- lifecycle -----------------------------------------------------------

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "NdClient":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    # -- service helpers -----------------------------------------------------

    @property
    def config(self) -> NdConfig:
        return self._config

    def manage_get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self.get(self._config.manage_base, path, params)

    def analyze_get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self.get(self._config.analyze_base, path, params)

    def one_manage_get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return self.get(self._config.one_manage_base, path, params)

    # -- core ----------------------------------------------------------------

    def get(
        self,
        base: str,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """GET `<base><path>` with auth; re-login once on a 401.

        Returns the parsed JSON body.

        Raises:
            NdApiError: on a non-success status.
            NdError: on a network error or invalid JSON.
        """
        url = base.rstrip("/") + "/" + path.lstrip("/")

        resp = self._send(url, params)
        if resp.status_code == 401:
            # Token may have expired — refresh once and retry.
            self._auth.invalidate()
            resp = self._send(url, params)

        if resp.status_code >= 400:
            raise NdApiError(
                f"ND GET {url} failed (HTTP {resp.status_code}): {_safe_message(resp)}",
                status_code=resp.status_code,
            )

        try:
            return resp.json()
        except ValueError as exc:
            raise NdError(f"ND GET {url} returned non-JSON content.") from exc

    def _send(self, url: str, params: dict[str, Any] | None) -> httpx.Response:
        try:
            return self._http.get(url, params=params, headers=self._auth.auth_headers())
        except httpx.HTTPError as exc:
            raise NdError(f"Network error calling ND GET {url}: {exc}") from exc


def _safe_message(resp: httpx.Response) -> str:
    try:
        body = resp.json()
    except ValueError:
        return resp.text[:300]
    if isinstance(body, dict):
        return str(body.get("message") or body.get("error") or body)[:300]
    return str(body)[:300]
