"""Shared error types for the ND live client."""

from __future__ import annotations


class NdError(RuntimeError):
    """Base class for ND client errors (network, auth, or API)."""


class NdAuthError(NdError):
    """Login failed or the session could not be established."""


class NdApiError(NdError):
    """ND returned a non-success HTTP status for a request."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
