"""ND live MCP server — a thin FastMCP wrapper over the `nd` client library.

Read-only (GET) access to a live Nexus Dashboard: fabrics, health, switches,
interfaces, VRFs, networks, and the embedded template library.

Run over stdio (default):
    uv run server.py

Configuration is read from ND_* environment variables (see .env.example).
All logging goes to STDERR — stdout is reserved for the MCP protocol.
"""

from __future__ import annotations

import logging
import sys

from fastmcp import FastMCP

from nd import ConfigError, NdClient, NdConfig, NdError
from nd.tools import fabrics, interfaces, networks, switches, templates, vrfs

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
logger = logging.getLogger("nd-live")

mcp = FastMCP(
    name="nd-live",
    instructions=(
        "Read-only access to a live Cisco Nexus Dashboard. Use nd_list_fabrics / "
        "nd_fabric_health for fabric status, nd_list_switches and "
        "nd_switch_interfaces for devices, nd_list_vrfs / nd_list_networks for "
        "overlays, and nd_list_templates / nd_get_template for the embedded "
        "template library. Results are compact by default; pass detail=true for "
        "full JSON on a specific item."
    ),
)

_client: NdClient | None = None


def _get_client() -> NdClient:
    """Lazily build a single shared client from the environment."""
    global _client
    if _client is None:
        _client = NdClient(NdConfig.from_env())
    return _client


def _run(fn, *args, **kwargs) -> str:
    """Invoke a tool function, mapping errors to readable messages."""
    try:
        return fn(_get_client(), *args, **kwargs)
    except ConfigError as exc:
        return f"Configuration error: {exc}"
    except NdError as exc:
        return f"ND error: {exc}"
    except Exception as exc:  # noqa: BLE001 - surface unexpected errors to the agent
        logger.exception("Unexpected error in %s", getattr(fn, "__name__", fn))
        return f"Unexpected error: {exc}"


# -- Fabrics + health --------------------------------------------------------


@mcp.tool()
def nd_list_fabrics(detail: bool = False, status: bool = True) -> str:
    """List fabrics with category, type, license, and overall HEALTH + SYNC.

    Set status=False to skip the per-fabric summary calls (faster, no HEALTH/SYNC).
    """
    return _run(fabrics.list_fabrics, detail=detail, status=status)


@mcp.tool()
def nd_get_fabric(name: str) -> str:
    """Get full details for a single fabric by name."""
    return _run(fabrics.get_fabric, name)


@mcp.tool()
def nd_fabric_health(fabric: str) -> str:
    """Per-switch telemetry-collection health for a fabric (fabric name required)."""
    return _run(fabrics.fabric_health, fabric=fabric)


# -- Switches + interfaces ---------------------------------------------------


@mcp.tool()
def nd_list_switches(fabric: str | None = None, detail: bool = False) -> str:
    """List switches, optionally scoped to a fabric."""
    return _run(switches.list_switches, fabric=fabric, detail=detail)


@mcp.tool()
def nd_switch_interfaces(fabric: str, switch_id: str, detail: bool = False) -> str:
    """List interfaces for a switch (by serial/id) in a fabric."""
    return _run(interfaces.switch_interfaces, fabric, switch_id, detail=detail)


# -- VRFs + networks ---------------------------------------------------------


@mcp.tool()
def nd_list_vrfs(fabric: str, detail: bool = False) -> str:
    """List VRFs in a fabric."""
    return _run(vrfs.list_vrfs, fabric, detail=detail)


@mcp.tool()
def nd_get_vrf(fabric: str, name: str) -> str:
    """Get full details for a single VRF."""
    return _run(vrfs.get_vrf, fabric, name)


@mcp.tool()
def nd_list_networks(fabric: str, detail: bool = False) -> str:
    """List networks in a fabric."""
    return _run(networks.list_networks, fabric, detail=detail)


@mcp.tool()
def nd_get_network(fabric: str, name: str) -> str:
    """Get full details for a single network."""
    return _run(networks.get_network, fabric, name)


# -- Templates ---------------------------------------------------------------


@mcp.tool()
def nd_list_templates(
    name_filter: str | None = None,
    template_type: str | None = None,
    max_results: int = 50,
) -> str:
    """List ND's embedded config templates (filter by name/type)."""
    return _run(
        templates.list_templates,
        name_filter=name_filter,
        template_type=template_type,
        max_results=max_results,
    )


@mcp.tool()
def nd_get_template(name: str) -> str:
    """Get a template's content and parameters by name."""
    return _run(templates.get_template, name)


if __name__ == "__main__":
    # stdio transport: stdout carries JSON-RPC only. Disable the FastMCP banner
    # (and its pypi update check) so nothing extra is emitted and startup does
    # not block on an outbound network call.
    mcp.run(show_banner=False)
