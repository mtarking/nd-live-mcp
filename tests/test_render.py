"""Render helpers: compact tables and the hard output-size guard."""

from __future__ import annotations

from nd.render import coerce_list, first, guard, table


def test_guard_truncates_with_hint() -> None:
    text = "x" * 1000
    out = guard(text, max_chars=300)
    assert len(out) < 1000
    assert "truncated" in out


def test_guard_passes_through_small_text() -> None:
    assert guard("short", max_chars=300) == "short"


def test_table_headers_and_row_count() -> None:
    out = table([["a", "1"], ["b", "2"]], ["NAME", "ID"], max_chars=8000)
    assert "NAME" in out and "ID" in out
    assert "(2 rows)" in out


def test_table_empty() -> None:
    assert table([], ["NAME"], max_chars=8000) == "(no results)"


def test_first_is_case_tolerant_and_skips_empty() -> None:
    item = {"Name": "", "fabricName": "DC1"}
    assert first(item, ["name", "fabricName"]) == "DC1"


def test_coerce_list_shapes() -> None:
    assert coerce_list({"fabrics": [{"a": 1}]}, "fabrics") == [{"a": 1}]
    assert coerce_list([{"a": 1}]) == [{"a": 1}]
    assert coerce_list({"a": 1}, "fabrics") == [{"a": 1}]
