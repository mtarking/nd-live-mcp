#!/usr/bin/env python3
"""Generate NaC-ND (Yamale) mini data models from LOCAL NDFC `.template` files.

Offline counterpart to `gen_policy_device_model.py`: instead of querying a live
ND, it reads raw `##template ...` DSL files from one or more directories, finds
the templates that carry a JSON-encoded (composite) parameter — a `struct`,
`structureArray`, or an array scalar (`type[]`) — and emits a Yamale schema
proposal modeled exactly like the live-ND generator:

  * a top-level map per template     (e.g. `tmpl_static_route_v4_v6:`)
  * `list(include('...'))` per structureArray, `include('...')` per struct
  * `list(<scalar>)` for array scalars (`string[]`, `ipAddress[]`, ...)
  * enum(validValues...) from the DSL
  * required=True only for unconditional `IsMandatory=true`

The field tree comes entirely from `nd_template_dsl.parse_variables` (there is no
API metadata offline). Emit/verify helpers are reused from the live generator so
the two paths cannot drift.

Usage:
    cd nd-live-mcp
    uv run --with yamale python scripts/gen_offline_template_model.py \
        [DIR ...] [--out PATH] [--prefix tmpl_]

Defaults to the two offline-template directories under nac-nd/docs/offline-templates/.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

# Reuse the DSL parser and the live generator's emit/verify helpers so the
# offline and live outputs stay identical in style.
from nd_template_dsl import parse_variables  # noqa: E402
from gen_policy_device_model import (  # noqa: E402
    SCALAR_MAP,
    _verify_schema,
    build_include,
    snake,
)

_DEFAULT_DIRS = [
    Path(__file__).resolve().parents[2]
    / "nac-nd/docs/offline-templates/ndfc_changed_template_files_only_part_01",
    Path(__file__).resolve().parents[2]
    / "nac-nd/docs/offline-templates/ndfc_changed_template_files_only_part_02",
]
_DEFAULT_OUT = (
    Path(__file__).resolve().parents[2]
    / "nac-nd/docs/specs/offline_templates.proposal.yaml"
)


def parse_properties(content: str) -> dict[str, str]:
    """Parse the `##template properties` block into a key/value dict."""
    start = content.find("##template properties")
    if start == -1:
        return {}
    end = content.find("##", start + len("##template properties"))
    block = content[start + len("##template properties") : end]
    props: dict[str, str] = {}
    for line in block.splitlines():
        if "=" in line:
            key, _, val = line.partition("=")
            props[key.strip()] = val.strip().rstrip(";").strip()
    return props


def is_composite(field: dict) -> bool:
    """A DSL field needs JSON encoding when it is a struct/array (never a scalar)."""
    t = str(field.get("type", "")).lower()
    return "struct" in t or t.endswith("[]")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dirs", nargs="*", type=Path, default=_DEFAULT_DIRS,
                    help="directories of .template files (default: the two offline dirs)")
    ap.add_argument("--out", type=Path, default=_DEFAULT_OUT, help="output schema path")
    ap.add_argument("--prefix", default="tmpl_", help="map/include name prefix")
    args = ap.parse_args(argv)

    files = sorted(
        {f for d in args.dirs for f in Path(d).glob("*.template")}
    )
    if not files:
        print(f"No .template files found under: {args.dirs}", file=sys.stderr)
        return 1

    scanned = 0
    templates: list[dict] = []
    for path in files:
        scanned += 1
        content = path.read_text(encoding="utf-8", errors="replace")
        props = parse_properties(content)
        name = props.get("name") or path.stem
        fields = parse_variables(content)
        comp = [f for f in fields if is_composite(f)]
        if comp:
            templates.append({
                "name": name,
                "type": props.get("templateType", "-"),
                "subtype": props.get("templateSubType", "-"),
                "file": path.name,
                "params": comp,
            })

    templates.sort(key=lambda t: t["name"].lower())

    includes: dict[str, list] = {}
    root_lines = [
        "# ── Root document: every template map is an OPTIONAL include so a data",
        "#    file sets only the templates it uses. Definitions follow the 2nd '---'.",
    ]
    body: list[str] = []
    report: list[dict] = []
    for t in templates:
        map_name = f"{args.prefix}{snake(t['name'])}"
        root_lines.append(f"{map_name}: include('{map_name}', required=False)")
        body.append(f"# ── {t['name']}  ({t['type']}/{t['subtype']})  [{t['file']}] "
                    + "─" * max(2, 40 - len(t['name'])))
        body.append(f"{map_name}:")
        rec_params = []
        for p in t["params"]:
            fld = snake(p["name"])
            ptype = p["type"].lower()
            rec_params.append({"name": p["name"], "type": p["type"]})
            if ptype.endswith("[]"):
                inner = SCALAR_MAP.get(ptype[:-2], "str()")
                body.append(f"  {fld}: list({inner}, required=False)   # {p['name']} ({p['type']})")
            elif "struct" in ptype:
                sub = p.get("fields") or []
                if not sub:
                    coll = "list(map()" if "array" in ptype else "map("
                    body.append(f"  {fld}: {coll}, required=False)   # {p['name']} ({p['type']}) — no sub-fields")
                    continue
                inc = f"{map_name}_{fld}"
                build_include(inc, sub, includes)
                if "array" in ptype:
                    body.append(f"  {fld}: list(include('{inc}'), required=False)   # {p['name']} ({p['type']})")
                else:
                    body.append(f"  {fld}: include('{inc}', required=False)   # {p['name']} ({p['type']})")
        body.append("")
        report.append({"name": t["name"], "templateType": t["type"],
                       "templateSubType": t["subtype"], "file": t["file"],
                       "composite_parameters": rec_params})

    header = [
        "# ==============================================================================",
        "# PROPOSAL — NaC-ND mini data models for JSON-encoded params (OFFLINE source)",
        "#",
        "# Auto-generated from local NDFC .template files by",
        "#   nd-live-mcp/scripts/gen_offline_template_model.py",
        "# Field tree parsed from the ##template variables DSL (no live ND). NOT wired",
        "# into nac-nd/schemas/schema.yaml — this is a proposal for review.",
        "#",
        "# Conventions:",
        "#   * two YAML documents: root references each template map as an include,",
        "#     then a '---' separator, then all include definitions (Yamale only",
        "#     registers named includes from documents AFTER the first '---').",
        "#   * snake_case field names; structureArray -> list(include(...));",
        "#     struct -> include(...); string[]/ipAddress[] -> list(str()).",
        "#   * enum(validValues...) from the DSL; required=True only for the literal",
        "#     IsMandatory=true (conditional mandatory -> nac-validate).",
        "#   * ip*/interface/mac types modeled as str() (conservative).",
        "# ==============================================================================",
        "---",
        "",
    ]
    root_lines.append("")
    root_lines.append("---")
    root_lines.append("")

    inc_lines = ["# ── include(...) definitions (struct elements) ─────────────────────────────"]
    for name in sorted(includes):
        inc_lines.append(f"{name}:")
        for fld, val in includes[name]:
            inc_lines.append(f"  {fld}: {val}")
        inc_lines.append("")

    if not templates:
        print(f"Scanned {scanned} templates; none carry a JSON-encoded parameter.")
        return 0

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(header + root_lines + body + inc_lines) + "\n", encoding="utf-8")
    _verify_schema(args.out)

    report_path = args.out.with_suffix(".composite_params.json")
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote proposal -> {args.out}")
    print(f"Wrote report   -> {report_path}")
    print(f"Scanned {scanned} templates; {len(templates)} have JSON-encoded params; "
          f"{len(includes)} struct includes.")
    print()
    print(f"{'TEMPLATE':40} {'TYPE':10} {'SUBTYPE':10} JSON-ENCODED PARAMETERS")
    print("-" * 100)
    for t in templates:
        params = ", ".join(f"{p['name']} ({p['type']})" for p in t["params"])
        print(f"{t['name'][:39]:40} {t['type'][:9]:10} {t['subtype'][:9]:10} {params}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
