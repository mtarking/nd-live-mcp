"""Fabric inventory (Manage) and fabric health (Analyze) tools."""

from __future__ import annotations

from ..client import NdClient
from ..errors import NdError
from ..render import as_json, coerce_list, first, table


def _fabric_status(client: NdClient, name: str) -> tuple[str, str]:
    """Return (health, sync) for a fabric from its summary endpoint.

    Degrades to ("-", "-") if the per-fabric summary call fails.
    """
    try:
        summary = client.manage_get(f"/fabrics/{name}/summary")
    except NdError:
        return "-", "-"
    health = first(summary, ["anomalyLevel", "advisoryLevel"])
    sync = first(
        summary,
        ["management.configSyncStatus.syncStatus", "connectivityStatus"],
    )
    return health, sync


def list_fabrics(client: NdClient, detail: bool = False, status: bool = True) -> str:
    """List fabrics with category, type, license, and overall health/sync.

    - detail: return full JSON of the fabric list instead of a compact table.
    - status: also fetch each fabric's summary for HEALTH (anomalyLevel) and
      SYNC (config-sync) columns. One extra call per fabric; set False to skip.
    """
    payload = client.manage_get("/fabrics")
    if detail:
        return as_json(payload, client.config.max_output_chars)

    records = coerce_list(payload, "fabrics")
    rows = []
    for f in records:
        name = first(f, ["name", "fabricName"])
        health, sync = ("-", "-")
        if status and name != "-":
            health, sync = _fabric_status(client, name)
        rows.append(
            [
                name,
                first(f, ["category"]),
                first(f, ["management.type", "type", "fabricType", "templateName"]),
                first(f, ["licenseTier", "license"]),
                health,
                sync,
            ]
        )
    return table(
        rows,
        ["NAME", "CATEGORY", "TYPE", "LICENSE", "HEALTH", "SYNC"],
        client.config.max_output_chars,
    )


def get_fabric(client: NdClient, name: str) -> str:
    """Get full details for a single fabric by name."""
    payload = client.manage_get(f"/fabrics/{name}")
    return as_json(payload, client.config.max_output_chars)


def fabric_health(client: NdClient, fabric: str) -> str:
    """Per-switch telemetry-collection health for a fabric (Analyze).

    - fabric: fabric name (required by the ND API).

    Reports the collection-pipeline state for each switch. A switch is summarised
    by how many telemetry resources are in each state, with any non-healthy ones
    called out.
    """
    payload = client.analyze_get(
        "/telemetry/healthSummary", params={"fabricName": fabric}
    )
    records = coerce_list(payload, "fabricHealthSummaryCollection")

    rows = []
    for sw in records:
        stats = sw.get("telemetryHealthStats") or []
        states: dict[str, int] = {}
        problems = []
        for s in stats:
            state = str(s.get("state", "?"))
            states[state] = states.get(state, 0) + 1
            if state.lower() not in {"success", "healthy"}:
                problems.append(f"{s.get('resource', '?')}={state}")
        summary = ", ".join(f"{k}:{v}" for k, v in sorted(states.items())) or "-"
        rows.append(
            [
                first(sw, ["switchName", "switch", "name"]),
                str(len(stats)),
                summary,
                ", ".join(problems) if problems else "-",
            ]
        )
    return table(
        rows,
        ["SWITCH", "RESOURCES", "STATES", "ISSUES"],
        client.config.max_output_chars,
    )
