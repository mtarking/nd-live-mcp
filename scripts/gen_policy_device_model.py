#!/usr/bin/env python3
"""Generate a NaC-ND (Yamale) data-model proposal for the JSON-encoded parameters
of policy/device config templates.

For every policy/device template that has a composite (JSON-encoded) parameter
(`structureArray`, `struct`, or an array type like `string[]` / `ipAddress[]`),
this emits a Yamale schema snippet modeled after `nac-nd/schemas/schema.yaml`:

  * a top-level map per template  (e.g. `policy_ip_acl:`)
  * `list(include('...'))` for each structureArray parameter
  * a dedicated `include(...)` definition for each struct element (recursively)
  * `list(<scalar>)` for array-of-scalar parameters (`string[]`, `ipAddress[]`)

Field naming is converted to snake_case. Field-level `required=True` is emitted
ONLY when the source parameter is *unconditionally* mandatory (`IsMandatory=true`);
conditionally-mandatory fields (`IsMandatory="EXPR"`) are left `required=False`
because value-conditional logic belongs in nac-validate, not Yamale.

Reuses the read-only `nd` client and the same ND_* env vars as the MCP server.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_REPO_ROOT = Path("/Users/mtarking/Documents/Development/DCN/nac/nd-as-code/nd-live-mcp")
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from nd.client import NdClient  # noqa: E402
from nd.config import NdConfig  # noqa: E402

SCRIPTS = _REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from nd_template_dsl import parse_variables  # noqa: E402

OUT = Path(
    "/Users/mtarking/Documents/Development/DCN/nac/nd-as-code/"
    "nac-nd/docs/specs/policy_device_templates.proposal.yaml"
)


def snake(name: str) -> str:
    """Convert camelCase / UPPER_SNAKE / mixed identifiers to snake_case."""
    # Normalise IPv4/IPv6 so they don't split into "i_pv6".
    name = name.replace("IPv4", "Ipv4").replace("IPv6", "Ipv6")
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    s = s.replace("-", "_")
    s = re.sub(r"_+", "_", s)
    return s.strip("_").lower()


def is_composite(p: dict) -> bool:
    t = str(p.get("parameterType", "")).lower()
    return "structure" in t or "array" in t or t.endswith("[]") or bool(
        p.get("structureParameters")
    )


# Map an ND scalar parameterType to a Yamale validator (without required=...).
SCALAR_MAP = {
    "string": "str()",
    "integer": "int()",
    "long": "int()",
    "boolean": "bool()",
    "interface": "str()",
    "interfacerange": "str()",
    "ipv4address": "str()",
    "ipv6address": "str()",
    "ipaddress": "str()",
    "ipv4addresswithsubnet": "str()",
    "ipv6addresswithsubnet": "str()",
    "ipv4addresswithoutprefix": "str()",
    "ipaddresswithoutprefix": "str()",
    "ipv6addresswithprefix": "str()",
    "ipaddresslist": "str()",
    "integerrange": "str()",
    "macaddress": "str()",
}


def field_required(field: dict) -> bool:
    return str(field.get("mandatory", "")).strip().strip('"').lower() == "true"


def with_required(validator: str, required: bool) -> str:
    """Splice `required=False` into a Yamale validator call when not required."""
    if required:
        return validator
    inner = validator[:-1]  # drop trailing ')'
    if inner.endswith("("):
        return inner + "required=False)"
    return inner + ", required=False)"


def validator_for(field: dict, includes: dict, prefix: str) -> str:
    """Return a Yamale validator string for a field, recursing into structures."""
    ptype = str(field.get("type", "")).lower()
    required = field_required(field)

    # array-of-scalar (string[], ipAddress[], ...)
    if ptype.endswith("[]"):
        inner = SCALAR_MAP.get(ptype[:-2], "str()")
        return with_required(f"list({inner})", required)

    # nested structure array / struct
    if "structure" in ptype or ptype == "struct":
        child_fields = field.get("fields") or []
        if not child_fields:
            # API did not expose sub-fields at this depth; accept a free-form map.
            if "array" in ptype:
                return with_required("list(map())", required)
            return with_required("map()", required)
        child_name = f"{prefix}_{snake(field['name'])}"
        build_include(child_name, child_fields, includes)
        if "array" in ptype:
            return with_required(f"list(include('{child_name}'))", required)
        return with_required(f"include('{child_name}')", required)

    # enum
    if ptype == "enum" and field.get("valid"):
        vals = ", ".join(f"'{v}'" for v in field["valid"].split(","))
        return with_required(f"enum({vals})", required)

    # plain scalar
    return with_required(SCALAR_MAP.get(ptype, "str()"), required)


def build_include(name: str, fields: list, includes: dict) -> None:
    """Register an include(...) definition for a struct's fields."""
    if name in includes:
        return
    lines = []
    for f in fields:
        lines.append((snake(f["name"]), validator_for(f, includes, name)))
    includes[name] = lines


def main() -> int:
    sel = json.loads((SCRIPTS / "json_encoded_params_policy_device.json").read_text())
    names = [r["name"] for r in sel]

    templates = []
    with NdClient(NdConfig.from_env()) as client:
        for n in names:
            d = client.manage_get(f"/configTemplates/{n}")
            # DSL fallback tree: recovers struct fields nested deeper than the API
            # metadata expands (the API stops at one level of structureArray).
            dsl_by_name = {f["name"]: f for f in parse_variables(d.get("content", ""))}
            comp = []
            for p in d.get("parameters", []):
                if is_composite(p):
                    comp.append(_walk(p, dsl_by_name.get(p.get("name"))))
            templates.append({"name": n, "type": d.get("templateType"),
                              "subtype": d.get("templateSubType"), "params": comp})

    includes: dict[str, list] = {}
    body: list[str] = []
    for t in templates:
        map_name = f"policy_{snake(t['name'])}"
        body.append(f"# ── {t['name']}  ({t['type']}/{t['subtype']}) "
                    + "─" * max(2, 60 - len(t['name'])))
        body.append(f"{map_name}:")
        for p in t["params"]:
            fld = snake(p["name"])
            ptype = p["type"].lower()
            if ptype.endswith("[]"):
                inner = SCALAR_MAP.get(ptype[:-2], "str()")
                body.append(f"  {fld}: list({inner}, required=False)   # {p['name']} ({p['type']})")
            elif "structure" in ptype or ptype == "struct":
                fields = p.get("fields") or []
                if not fields:
                    coll = "list(map()" if "array" in ptype else "map("
                    body.append(f"  {fld}: {coll}, required=False)   # {p['name']} ({p['type']}) — no sub-fields exposed")
                    continue
                inc = f"{map_name}_{fld}"
                build_include(inc, fields, includes)
                if "array" in ptype:
                    body.append(f"  {fld}: list(include('{inc}'), required=False)   # {p['name']} ({p['type']})")
                else:
                    body.append(f"  {fld}: include('{inc}', required=False)   # {p['name']} ({p['type']})")
        body.append("")

    header = [
        "# ==============================================================================",
        "# PROPOSAL — NaC-ND data model for policy/device template JSON-encoded params",
        "#",
        "# Auto-generated from the live ND config-template library by",
        "#   nd-live-mcp/scripts/gen_policy_device_model.py",
        "# Modeled after nac-nd/schemas/schema.yaml (Yamale). NOT wired into the live",
        "# schema — this is a proposal for review.",
        "#",
        "# Conventions:",
        "#   * snake_case field names (source template uses camelCase / UPPER_SNAKE)",
        "#   * structureArray  -> list(include('<map>_<param>'))",
        "#   * struct          -> include('<map>_<param>')",
        "#   * string[]/ipAddress[] -> list(str())",
        "#   * enum(validValues...) from the template's validValues",
        "#   * required=True only where the source field is UNCONDITIONALLY mandatory;",
        "#     conditional mandatory (IsShow/IsMandatory expressions) -> nac-validate.",
        "#   * ip*/interface/mac types modeled as str() (regex belongs in a follow-up",
        "#     verbatim port or nac-validate), matching schema.yaml's conservative style.",
        "# ==============================================================================",
        "---",
        "",
    ]

    inc_lines = ["", "# ── include(...) definitions (struct elements) ─────────────────────────────"]
    for name in sorted(includes):
        inc_lines.append(f"{name}:")
        for fld, val in includes[name]:
            inc_lines.append(f"  {fld}: {val}")
        inc_lines.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(header + body + inc_lines) + "\n", encoding="utf-8")
    print(f"Wrote proposal -> {OUT}")
    print(f"Templates: {len(templates)}  include defs: {len(includes)}")
    return 0


def _walk(param: dict, dsl_node: dict | None = None) -> dict:
    """Recursively capture a composite param's nested fields.

    `dsl_node` is the matching field parsed from the template `content` DSL. It is
    used as a fallback source when the ND API metadata does not expand a nested
    struct (the API stops after one level of `structureArray`).
    """
    sp = param.get("structureParameters") or {}
    dsl_children = {f["name"]: f for f in (dsl_node or {}).get("fields", [])}
    fields = []
    for fn, fv in sp.items():
        name = fv.get("name", fn)
        entry = {
            "name": name,
            "type": fv.get("parameterType"),
            "mandatory": str(fv.get("annotations", {}).get("IsMandatory", "")),
            "valid": fv.get("metaProperties", {}).get("validValues"),
        }
        child_dsl = dsl_children.get(name)
        if fv.get("structureParameters"):
            entry["fields"] = _walk(fv, child_dsl)["fields"]
        elif is_composite(fv) and child_dsl and child_dsl.get("fields"):
            # API did not expand this nested struct — recover it from the DSL.
            entry["fields"] = child_dsl["fields"]
        fields.append(entry)
    return {"name": param.get("name"), "type": param.get("parameterType"), "fields": fields}


if __name__ == "__main__":
    raise SystemExit(main())
