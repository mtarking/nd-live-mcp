"""Interface tools (Manage: per-switch config/oper state)."""

from __future__ import annotations

from ..client import NdClient
from ..render import as_json, coerce_list, first, table


def switch_interfaces(
    client: NdClient,
    fabric: str,
    switch_id: str,
    detail: bool = False,
) -> str:
    """List interfaces for a switch in a fabric.

    - fabric: fabric name.
    - switch_id: switch serial number / id.
    - detail: return full JSON instead of a compact table.
    """
    payload = client.manage_get(f"/fabrics/{fabric}/switches/{switch_id}/interfaces")
    if detail:
        return as_json(payload, client.config.max_output_chars)

    records = coerce_list(payload, "interfaces")
    rows = [
        [
            first(i, ["interfaceName", "ifName", "name"]),
            first(i, ["operData.adminStatus", "adminStatus", "adminState"]),
            first(i, ["operData.operationalStatus", "operStatus", "operState", "status"]),
            first(i, ["interfaceType", "ifType", "type"]),
            first(i, ["operData.operationalDescription", "description", "descr"]),
        ]
        for i in records
    ]
    return table(
        rows,
        ["INTERFACE", "ADMIN", "OPER", "TYPE", "DESCRIPTION"],
        client.config.max_output_chars,
    )
