"""Resource-manager tools (Manage).

Read-only access to pool allocations (ID / IP / SUBNET) via
``GET /api/v1/manage/fabrics/{fabricName}/resources``. Useful for inspecting
how ND allocates fabric resources — vPC domain IDs, underlay IPs, L3 VNIs,
loopbacks, anycast VIPs — including the real ``poolName``, ``entityName``
format, and ``scopeType`` used by each allocation.
"""

from __future__ import annotations

from ..client import NdClient
from ..render import as_json, coerce_list, first, table


def list_resources(
    client: NdClient,
    fabric: str,
    pool_name: str | None = None,
    switch_id: str | None = None,
    pre_allocated: bool | None = None,
    detail: bool = False,
) -> str:
    """List resource-manager allocations in a fabric.

    - fabric: fabric name.
    - pool_name: optional poolName filter (e.g. a vPC domain-ID pool).
    - switch_id: optional switchId filter (serial / management IP).
    - pre_allocated: optional; True/False maps to filter=isPreAllocated:<bool>.
    - detail: return full JSON instead of a compact table.
    """
    params: dict[str, str] = {}
    if pool_name:
        params["poolName"] = pool_name
    if switch_id:
        params["switchId"] = switch_id
    if pre_allocated is not None:
        params["filter"] = f"isPreAllocated:{str(pre_allocated).lower()}"

    payload = client.manage_get(f"/fabrics/{fabric}/resources", params=params or None)
    if detail:
        return as_json(payload, client.config.max_output_chars)

    records = coerce_list(payload, "resources")
    rows = [
        [
            first(r, ["entityName"]),
            first(r, ["poolName"]),
            first(r, ["scopeDetails.scopeType", "scopeType"]),
            first(r, ["resourceValue", "resourceId"]),
            first(r, ["isPreAllocated"]),
            first(r, ["vrfName"]),
        ]
        for r in records
    ]
    return table(
        rows,
        ["ENTITY", "POOL", "SCOPE", "VALUE", "PRE-ALLOC", "VRF"],
        client.config.max_output_chars,
    )
