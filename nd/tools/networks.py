"""Network tools (Manage)."""

from __future__ import annotations

from ..client import NdClient
from ..render import as_json, coerce_list, first, table


def list_networks(client: NdClient, fabric: str, detail: bool = False) -> str:
    """List networks in a fabric.

    - fabric: fabric name.
    - detail: return full JSON instead of a compact table.
    """
    payload = client.manage_get(f"/fabrics/{fabric}/networks")
    if detail:
        return as_json(payload, client.config.max_output_chars)

    records = coerce_list(payload, "networks")
    rows = [
        [
            first(n, ["networkName", "name"]),
            first(n, ["networkId", "id", "networkSegmentId", "vni"]),
            first(n, ["vlanId", "vlan"]),
            first(n, ["vrf", "vrfName"]),
            first(n, ["networkStatus", "status"]),
        ]
        for n in records
    ]
    return table(
        rows,
        ["NETWORK", "ID", "VLAN", "VRF", "STATUS"],
        client.config.max_output_chars,
    )


def get_network(client: NdClient, fabric: str, name: str) -> str:
    """Get full details for a single network."""
    payload = client.manage_get(f"/fabrics/{fabric}/networks/{name}")
    return as_json(payload, client.config.max_output_chars)
