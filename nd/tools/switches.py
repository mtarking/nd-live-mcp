"""Switch / device inventory tools (Manage)."""

from __future__ import annotations

from ..client import NdClient
from ..render import as_json, coerce_list, first, table


def list_switches(client: NdClient, fabric: str | None = None, detail: bool = False) -> str:
    """List switches, optionally scoped to a fabric.

    - fabric: restrict to one fabric (uses the per-fabric endpoint).
    - detail: return full JSON instead of a compact table.
    """
    path = f"/fabrics/{fabric}/switches" if fabric else "/inventory/switches"
    payload = client.manage_get(path)
    if detail:
        return as_json(payload, client.config.max_output_chars)

    records = coerce_list(payload, "switches", "switchesData")
    rows = [
        [
            first(s, ["hostname", "hostName", "logicalName", "name", "sysName"]),
            first(s, ["fabricManagementIp", "ipAddress", "mgmtIpAddress", "oobIpAddress"]),
            first(s, ["serialNumber", "serial", "switchId"]),
            first(s, ["model", "platform"]),
            first(s, ["switchRole", "role"]),
            first(
                s,
                [
                    "additionalData.discoveryStatus",
                    "status",
                    "operStatus",
                    "anomalyLevel",
                ],
            ),
            first(
                s,
                [
                    "additionalData.configSyncStatus",
                    "configSyncStatus",
                    "syncStatus",
                    "deploymentStatus",
                ],
            ),
        ]
        for s in records
    ]
    return table(
        rows,
        ["HOSTNAME", "IP", "SERIAL", "MODEL", "ROLE", "STATUS", "SYNC"],
        client.config.max_output_chars,
    )
