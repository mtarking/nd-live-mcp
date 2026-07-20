"""VRF tools (Manage)."""

from __future__ import annotations

from ..client import NdClient
from ..render import as_json, coerce_list, first, table


def list_vrfs(client: NdClient, fabric: str, detail: bool = False) -> str:
    """List VRFs in a fabric.

    - fabric: fabric name.
    - detail: return full JSON instead of a compact table.
    """
    payload = client.manage_get(f"/fabrics/{fabric}/vrfs")
    if detail:
        return as_json(payload, client.config.max_output_chars)

    records = coerce_list(payload, "vrfs")
    rows = [
        [
            first(v, ["vrfName", "name"]),
            first(v, ["vrfId", "id", "vrfSegmentId"]),
            first(v, ["vrfVlanId", "vlanId"]),
            first(v, ["vrfStatus", "status"]),
        ]
        for v in records
    ]
    return table(
        rows,
        ["VRF", "ID", "VLAN", "STATUS"],
        client.config.max_output_chars,
    )


def get_vrf(client: NdClient, fabric: str, name: str) -> str:
    """Get full details for a single VRF."""
    payload = client.manage_get(f"/fabrics/{fabric}/vrfs/{name}")
    return as_json(payload, client.config.max_output_chars)
