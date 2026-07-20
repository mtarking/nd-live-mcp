"""Output shaping for token efficiency.

Tools return compact text by default; callers pass `detail=True` for full JSON.
Every tool result passes through `guard()` so a huge ND payload can never blow
up the model's context.
"""

from __future__ import annotations

import json
from typing import Any, Iterable, Sequence

_TRUNCATION_HINT = (
    "\n... output truncated ({shown} of {total} chars). "
    "Narrow the query (filters / a specific name) or the caller can raise "
    "ND_MAX_OUTPUT_CHARS."
)


def guard(text: str, max_chars: int) -> str:
    """Truncate text to `max_chars`, appending a hint when it is cut."""
    if max_chars <= 0 or len(text) <= max_chars:
        return text
    keep = max(0, max_chars - 200)
    return text[:keep] + _TRUNCATION_HINT.format(shown=keep, total=len(text))


def as_json(obj: Any, max_chars: int) -> str:
    """Pretty-print a JSON object, guarded."""
    return guard(json.dumps(obj, indent=2, default=str), max_chars)


def table(rows: Sequence[Sequence[str]], headers: Sequence[str], max_chars: int) -> str:
    """Render a compact fixed-width table, guarded.

    Empty row sets return a friendly message instead of an empty table.
    """
    if not rows:
        return "(no results)"

    cols = len(headers)
    widths = [len(h) for h in headers]
    str_rows: list[list[str]] = []
    for row in rows:
        cells = [("" if c is None else str(c)) for c in row][:cols]
        cells += [""] * (cols - len(cells))
        str_rows.append(cells)
        for i, cell in enumerate(cells):
            widths[i] = max(widths[i], len(cell))

    def fmt(cells: Sequence[str]) -> str:
        return "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells)).rstrip()

    lines = [fmt(list(headers)), fmt(["-" * w for w in widths])]
    lines.extend(fmt(cells) for cells in str_rows)
    lines.append(f"\n({len(str_rows)} row{'s' if len(str_rows) != 1 else ''})")
    return guard("\n".join(lines), max_chars)


def dig(item: dict[str, Any], key: str) -> Any:
    """Look up `key` in a dict, supporting dotted paths and case-tolerance.

    `"management.type"` traverses nested dicts; a bare key falls back to a
    case-insensitive top-level match.
    """
    if "." in key:
        cur: Any = item
        for part in key.split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return None
        return cur
    if key in item:
        return item[key]
    lowered = {k.lower(): v for k, v in item.items()}
    return lowered.get(key.lower())


def first(item: dict[str, Any], keys: Iterable[str], default: str = "-") -> str:
    """Return the first present, non-empty value among `keys`.

    Supports dotted paths (e.g. `"management.type"`) and case-tolerant top-level keys.
    """
    for key in keys:
        value = dig(item, key)
        if value not in (None, "", [], {}):
            return str(value)
    return default


def coerce_list(payload: Any, *keys: str) -> list[dict[str, Any]]:
    """Extract a list of records from a variable ND response shape.

    Handles `{key: [...]}`, a bare `[...]`, or a single object. When a named
    key is present but null/empty (e.g. an empty fabric), returns `[]` rather
    than fabricating a row from the wrapper object.
    """
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in keys:
            if key in payload:
                value = payload.get(key)
                if isinstance(value, list):
                    return [x for x in value if isinstance(x, dict)]
                return []
        return [payload]
    return []
