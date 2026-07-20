"""Embedded template library tools (Manage: /configTemplates)."""

from __future__ import annotations

from ..client import NdClient
from ..render import as_json, coerce_list, first, table


def list_templates(
    client: NdClient,
    name_filter: str | None = None,
    template_type: str | None = None,
    max_results: int = 50,
) -> str:
    """List ND's embedded config templates.

    - name_filter: server-side substring/name filter.
    - template_type: e.g. exec, fabric, policy, profile, report, show.
    - max_results: cap the number returned (default 50).
    """
    params: dict[str, str | int] = {"max": max_results}
    if name_filter:
        params["filter"] = name_filter
    payload = client.manage_get("/configTemplates", params=params)

    records = coerce_list(payload, "templates")
    if template_type:
        tt = template_type.lower()
        records = [
            r for r in records if first(r, ["templateType", "type"]).lower() == tt
        ]
    rows = [
        [
            first(t, ["name", "templateName"]),
            first(t, ["templateType", "type"]),
            first(t, ["templateSubType", "subType"]),
            first(t, ["contentType"]),
            first(t, ["description", "desc"]),
        ]
        for t in records
    ]
    return table(
        rows,
        ["NAME", "TYPE", "SUBTYPE", "CONTENT", "DESCRIPTION"],
        client.config.max_output_chars,
    )


def get_template(client: NdClient, name: str) -> str:
    """Get a template's content and parameters by name."""
    payload = client.manage_get(f"/configTemplates/{name}")
    return as_json(payload, client.config.max_output_chars)
