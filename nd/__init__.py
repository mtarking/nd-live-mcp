"""Read-only live Nexus Dashboard (ND) client library.

The MCP server (`server.py`) is a thin wrapper over this package. The same code
is imported directly by tests and pipeline checks — MCP and CI share the code,
not the execution path.
"""

from __future__ import annotations

from .client import NdClient
from .config import ConfigError, NdConfig
from .errors import NdApiError, NdAuthError, NdError

__all__ = [
    "NdClient",
    "NdConfig",
    "ConfigError",
    "NdError",
    "NdAuthError",
    "NdApiError",
]
