"""Minimal parser for the ND config-template DSL `##template variables` block.

The unified ND API (`/configTemplates/{name}`) only expands **one** level of
`structureArray` nesting in its `parameters[].structureParameters` metadata. For
structs nested inside another struct (e.g. `route_map_enhanced` entries ->
`ruleEntries`, or `sgm` groups -> `interfaces`), the field definitions exist only
in the template `content` DSL. This parser recovers those nested fields.

It returns the same shape the generator already consumes:
    {"name", "type", "mandatory", "valid", "fields"(optional)}

Scope: intentionally small — it handles the constructs that appear in the ND
policy/device templates (scalar decls, `enum ... { validValues=...; }`,
`type[] name;` arrays, and `struct [Tag] { ... } name[];`). It is validated
against a known API case (`ip_acl.ACES`) before use.
"""

from __future__ import annotations

import re


def _strip_line_comments(text: str) -> str:
    out = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        out.append(line)
    return "\n".join(out)


def _find_matching(text: str, open_idx: int, open_ch: str, close_ch: str) -> int:
    """Return index of the matching close char for the opener at open_idx,
    honouring double-quoted strings (so ')' or '}' inside quotes don't count)."""
    depth = 0
    i = open_idx
    in_str = False
    while i < len(text):
        ch = text[i]
        if in_str:
            if ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _mandatory(annotation: str) -> str:
    m = re.search(r'IsMandatory\s*=\s*(true|false|"[^"]*")', annotation)
    if not m:
        return ""
    return "true" if m.group(1) == "true" else ""


def _valid_values(block: str) -> str | None:
    m = re.search(r"validValues\s*=\s*([^;]+);", block)
    return m.group(1).strip() if m else None


def parse_fields(text: str, start: int, end: int) -> tuple[list[dict], int]:
    """Parse field declarations in text[start:end]; stop at an unmatched '}'.

    Returns (fields, index_of_terminating_brace_or_end).
    """
    fields: list[dict] = []
    pending_annotation = ""
    i = start
    while i < end:
        ch = text[i]
        if ch.isspace() or ch == ";":
            i += 1
            continue
        if ch == "}":
            return fields, i
        if ch == "@" and text[i : i + 2] == "@(":
            close = _find_matching(text, i + 1, "(", ")")
            pending_annotation = text[i : close + 1]
            i = close + 1
            continue

        # read a leading identifier (type keyword or 'struct'/'enum')
        m = IDENT.match(text, i)
        if not m:
            i += 1
            continue
        keyword = m.group(0)
        j = m.end()

        if keyword == "struct":
            # optional tag name, then '{ ... }', then varname[optional []] ';'
            tag = IDENT.match(text, _skip_ws(text, j))
            k = tag.end() if tag else j
            brace = text.index("{", k)
            close = _find_matching(text, brace, "{", "}")
            inner, _ = parse_fields(text, brace + 1, close)
            after = _skip_ws(text, close + 1)
            var = IDENT.match(text, after)
            name = var.group(0) if var else (tag.group(0) if tag else "struct")
            rest_end = text.index(";", close + 1)
            is_array = "[]" in text[after:rest_end]
            fields.append({
                "name": name,
                "type": "structureArray" if is_array else "struct",
                "mandatory": _mandatory(pending_annotation),
                "valid": None,
                "fields": inner,
            })
            pending_annotation = ""
            i = rest_end + 1
            continue

        if keyword == "enum":
            var = IDENT.match(text, _skip_ws(text, j))
            name = var.group(0)
            brace = text.index("{", var.end())
            close = _find_matching(text, brace, "{", "}")
            block = text[brace + 1 : close]
            rest_end = text.index(";", close + 1)
            fields.append({
                "name": name,
                "type": "enum",
                "mandatory": _mandatory(pending_annotation),
                "valid": _valid_values(block),
            })
            pending_annotation = ""
            i = rest_end + 1
            continue

        # scalar: TYPE[optional []] NAME [ { ... } ] ';'
        ptype = keyword
        after_type = j
        if text[j : j + 2] == "[]":
            ptype = keyword + "[]"
            after_type = j + 2
        var = IDENT.match(text, _skip_ws(text, after_type))
        if not var:
            i = j
            continue
        name = var.group(0)
        nxt = _skip_ws(text, var.end())
        if nxt < end and text[nxt] == "{":
            close = _find_matching(text, nxt, "{", "}")
            rest_end = text.index(";", close + 1)
        else:
            rest_end = text.index(";", var.end())
        fields.append({
            "name": name,
            "type": ptype,
            "mandatory": _mandatory(pending_annotation),
            "valid": None,
        })
        pending_annotation = ""
        i = rest_end + 1
    return fields, end


def _skip_ws(text: str, i: int) -> int:
    while i < len(text) and text[i].isspace():
        i += 1
    return i


def parse_variables(content: str) -> list[dict]:
    """Parse the top-level ##template variables block into a field tree."""
    start = content.find("##template variables")
    if start == -1:
        return []
    start += len("##template variables")
    end = content.find("##template content", start)
    if end == -1:
        end = content.find("\n##", start)
    block = _strip_line_comments(content[start:end])
    fields, _ = parse_fields(block, 0, len(block))
    return fields


def find_struct(fields: list[dict], name: str) -> dict | None:
    """Depth-first search for a struct/structureArray field by name."""
    for f in fields:
        if f.get("name") == name and f.get("fields") is not None:
            return f
        if f.get("fields"):
            hit = find_struct(f["fields"], name)
            if hit:
                return hit
    return None
