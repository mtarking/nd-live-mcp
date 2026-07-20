"""Configuration for the ND live client, loaded from environment variables.

Secrets come from the environment (or an OS keychain that populates the
environment) — never from tool arguments or chat.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be a number, got {raw!r}") from exc


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer, got {raw!r}") from exc


@dataclass(frozen=True)
class NdConfig:
    """Connection + behaviour settings for a single ND cluster."""

    host: str
    username: str
    password: str
    domain: str = "local"
    verify_tls: bool = True
    timeout: float = 30.0
    max_output_chars: int = 8000
    # Service base paths (defaults match the ND 4.2.1 unified API `servers` blocks).
    login_path: str = "/api/v1/infra/login"
    manage_base: str = "/api/v1/manage"
    analyze_base: str = "/api/v1/analyze"
    infra_base: str = "/api/v1/infra"
    one_manage_base: str = "/api/v1/oneManage"

    @classmethod
    def from_env(cls) -> "NdConfig":
        """Build a config from ND_* environment variables.

        Raises:
            ConfigError: if any required variable (host/username/password) is unset.
        """
        host = os.environ.get("ND_HOST", "").strip().rstrip("/")
        username = os.environ.get("ND_USERNAME", "").strip()
        password = os.environ.get("ND_PASSWORD", "")

        missing = [
            name
            for name, value in (
                ("ND_HOST", host),
                ("ND_USERNAME", username),
                ("ND_PASSWORD", password),
            )
            if not value
        ]
        if missing:
            raise ConfigError(
                "Missing required environment variable(s): "
                + ", ".join(missing)
                + ". See .env.example."
            )

        return cls(
            host=host,
            username=username,
            password=password,
            domain=os.environ.get("ND_DOMAIN", "local").strip() or "local",
            verify_tls=_env_bool("ND_VERIFY_TLS", True),
            timeout=_env_float("ND_TIMEOUT", 30.0),
            max_output_chars=_env_int("ND_MAX_OUTPUT_CHARS", 8000),
            login_path=os.environ.get("ND_LOGIN_PATH", "/api/v1/infra/login"),
            manage_base=os.environ.get("ND_MANAGE_BASE", "/api/v1/manage"),
            analyze_base=os.environ.get("ND_ANALYZE_BASE", "/api/v1/analyze"),
            infra_base=os.environ.get("ND_INFRA_BASE", "/api/v1/infra"),
            one_manage_base=os.environ.get("ND_ONE_MANAGE_BASE", "/api/v1/oneManage"),
        )
