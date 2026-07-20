#!/usr/bin/env python3
"""Find ND config-template parameters that must be JSON-encoded when sent to the API.

A template parameter must be passed to `/api/v1/manage/configTemplates` as a JSON-encoded
string (rather than a bare scalar) when it is a *composite* type: a structure, an
array-of-structure, or any array-valued parameter. Scalar parameters (`string`, `integer`,
`enum`, ...) are passed inline.

This script reuses the read-only `nd` client library that backs the `nd-live` MCP server, so
it authenticates from the same `ND_*` environment variables:

    ND_HOST, ND_USERNAME, ND_PASSWORD, ND_DOMAIN, ND_VERIFY_TLS

Usage:
    cd nd-live-mcp
    .venv/bin/python scripts/find_json_encoded_params.py
    .venv/bin/python scripts/find_json_encoded_params.py --output-md scripts/report.md
    .venv/bin/python scripts/find_json_encoded_params.py --output-json scripts/report.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Make the `nd` package importable when this script is run from anywhere.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from nd.client import NdClient  # noqa: E402
from nd.config import NdConfig  # noqa: E402


def is_composite(param: dict[str, Any]) -> bool:
    """Return True if a parameter carries a nested/array value (needs JSON encoding).

    Detection keys off the API's own type metadata — never off the parameter name:
      * parameterType contains "structure" (e.g. "structure", "structureArray")
      * parameterType is array-valued ("[]" suffix or contains "array")
      * structureParameters is a non-empty object (nested fields present)
    """
    ptype = str(param.get("parameterType", "")).strip().lower()
    if "structure" in ptype or "array" in ptype or ptype.endswith("[]"):
        return True
    struct_params = param.get("structureParameters")
    if isinstance(struct_params, dict) and struct_params:
        return True
    return False


def list_all_templates(client: NdClient, page_size: int = 5000) -> list[dict[str, Any]]:
    """Return every template summary from /configTemplates."""
    payload = client.manage_get("/configTemplates", params={"max": page_size})
    if isinstance(payload, dict):
        templates = payload.get("templates", [])
    elif isinstance(payload, list):
        templates = payload
    else:
        templates = []
    return [t for t in templates if isinstance(t, dict)]


def scan(client: NdClient) -> list[dict[str, Any]]:
    """Return one record per template that has >=1 composite parameter."""
    results: list[dict[str, Any]] = []
    templates = list_all_templates(client)
    total = len(templates)
    for idx, summary in enumerate(templates, start=1):
        name = summary.get("name") or summary.get("templateName")
        if not name:
            continue
        print(f"[{idx}/{total}] {name}", file=sys.stderr)
        try:
            detail = client.manage_get(f"/configTemplates/{name}")
        except Exception as exc:  # noqa: BLE001 - report and continue
            print(f"    ! failed: {exc}", file=sys.stderr)
            continue

        composite = [
            {"name": p.get("name"), "parameterType": p.get("parameterType")}
            for p in detail.get("parameters", [])
            if is_composite(p)
        ]
        if composite:
            results.append(
                {
                    "name": name,
                    "templateType": detail.get("templateType")
                    or summary.get("templateType"),
                    "templateSubType": detail.get("templateSubType")
                    or summary.get("templateSubType"),
                    "contentType": detail.get("contentType")
                    or summary.get("contentType"),
                    "composite_parameters": composite,
                }
            )
    results.sort(key=lambda r: r["name"].lower())
    return results


def render_table(results: list[dict[str, Any]]) -> str:
    """Render an aligned text table for the console."""
    rows = [
        (
            r["name"],
            str(r.get("templateType") or ""),
            str(r.get("templateSubType") or ""),
            ", ".join(
                f"{p['name']} ({p['parameterType']})" for p in r["composite_parameters"]
            ),
        )
        for r in results
    ]
    headers = ("TEMPLATE", "TYPE", "SUBTYPE", "JSON-ENCODED PARAMETERS")
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    # Cap the last column so the table stays readable.
    widths[3] = min(widths[3], 90)

    def fmt(row: tuple[str, ...]) -> str:
        return "  ".join(cell.ljust(widths[i])[: widths[i]] for i, cell in enumerate(row))

    lines = [fmt(headers), fmt(tuple("-" * w for w in widths))]
    lines += [fmt(row) for row in rows]
    return "\n".join(lines)


def render_markdown(results: list[dict[str, Any]]) -> str:
    """Render a Markdown report."""
    lines = [
        "# Templates with JSON-encoded (composite) parameters",
        "",
        f"Total templates flagged: **{len(results)}**",
        "",
        "| Template | Type | SubType | JSON-encoded parameters |",
        "| --- | --- | --- | --- |",
    ]
    for r in results:
        params = "<br>".join(
            f"`{p['name']}` ({p['parameterType']})" for p in r["composite_parameters"]
        )
        lines.append(
            f"| `{r['name']}` | {r.get('templateType') or ''} "
            f"| {r.get('templateSubType') or ''} | {params} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-md", type=Path, help="Write a Markdown report to this path.")
    parser.add_argument("--output-json", type=Path, help="Write a JSON report to this path.")
    args = parser.parse_args()

    with NdClient(NdConfig.from_env()) as client:
        results = scan(client)

    print(render_table(results))
    print(f"\n{len(results)} template(s) have at least one JSON-encoded parameter.")

    if args.output_md:
        args.output_md.write_text(render_markdown(results), encoding="utf-8")
        print(f"Wrote Markdown report -> {args.output_md}")
    if args.output_json:
        args.output_json.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"Wrote JSON report -> {args.output_json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
