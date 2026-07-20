"""Auth + client behaviour: login, token reuse, and 401 refresh."""

from __future__ import annotations

import httpx
import pytest

from nd import NdApiError, NdAuthError, NdClient, NdConfig


@pytest.fixture
def config() -> NdConfig:
    return NdConfig(host="https://nd.test", username="admin", password="pw", verify_tls=False)


def test_login_sends_credentials_and_caches_token(config: NdConfig) -> None:
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == config.login_path:
            import json

            seen["body"] = json.loads(request.content)
            seen["login_calls"] = seen.get("login_calls", 0) + 1
            return httpx.Response(200, json={"jwttoken": "tok"})
        assert request.headers.get("Authorization") == "Bearer tok"
        return httpx.Response(200, json={"fabrics": []})

    with NdClient(config, transport=httpx.MockTransport(handler)) as client:
        client.manage_get("/fabrics")
        client.manage_get("/fabrics")  # token reused, not re-fetched

    assert seen["body"] == {"userName": "admin", "userPasswd": "pw", "domain": "local"}
    assert seen["login_calls"] == 1


def test_401_triggers_single_reauth(config: NdConfig) -> None:
    state = {"gets": 0, "logins": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == config.login_path:
            state["logins"] += 1
            return httpx.Response(200, json={"jwttoken": f"tok{state['logins']}"})
        state["gets"] += 1
        if state["gets"] == 1:
            return httpx.Response(401, json={"message": "expired"})
        return httpx.Response(200, json={"fabrics": []})

    with NdClient(config, transport=httpx.MockTransport(handler)) as client:
        client.manage_get("/fabrics")

    assert state["logins"] == 2  # initial + one refresh
    assert state["gets"] == 2  # original + retry


def test_login_failure_raises_authuerror_without_leaking_password(config: NdConfig) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"message": "invalid credentials"})

    with NdClient(config, transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(NdAuthError) as exc:
            client.manage_get("/fabrics")
    assert "pw" not in str(exc.value)


def test_api_error_on_500(config: NdConfig) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == config.login_path:
            return httpx.Response(200, json={"jwttoken": "tok"})
        return httpx.Response(500, json={"message": "boom"})

    with NdClient(config, transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(NdApiError) as exc:
            client.manage_get("/fabrics")
    assert exc.value.status_code == 500
