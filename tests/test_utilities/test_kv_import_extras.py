from pathlib import Path

from mmx_engineering_spec_manager.utilities import kv_import


def test_read_json_list_of_scalars(tmp_path: Path):
    p = tmp_path / "arr.json"
    p.write_text("[1,2,3]", encoding="utf-8")
    rows = kv_import.read_json(p)
    assert rows == [{"value": 1}, {"value": 2}, {"value": 3}]


def test_read_json_dict_of_dicts(tmp_path: Path):
    p = tmp_path / "map.json"
    p.write_text('{"a": {"x": 1}, "b": {"y": 2}}', encoding="utf-8")
    rows = kv_import.read_json(p)
    # Should include key column and merge values
    assert any(r.get("key") == "a" and r.get("x") == 1 for r in rows)
    assert any(r.get("key") == "b" and r.get("y") == 2 for r in rows)


def test_read_json_dict_of_scalars_and_scalar(tmp_path: Path):
    p1 = tmp_path / "map2.json"
    p1.write_text('{"a": 1, "b": 2}', encoding="utf-8")
    rows1 = kv_import.read_json(p1)
    assert {r["key"] for r in rows1} == {"a", "b"}

    p2 = tmp_path / "scalar.json"
    p2.write_text('123', encoding="utf-8")
    rows2 = kv_import.read_json(p2)
    assert rows2 == [{"value": 123}]


def test_read_json_invalid_returns_text_wrapper(tmp_path: Path):
    p = tmp_path / "bad.json"
    content = "not-json at all"
    p.write_text(content, encoding="utf-8")
    rows = kv_import.read_json(p)
    assert rows == [{"value": content}]


def test_read_any_unknown_suffix_json_then_csv_fallback(tmp_path: Path):
    # Case 1: unknown suffix but JSON content parses
    p1 = tmp_path / "data.dat"
    p1.write_text('[{"a":1}]', encoding="utf-8")
    rows1 = kv_import.read_any(p1)
    assert rows1 and isinstance(rows1, list) and isinstance(rows1[0], dict)

    # Case 2: unknown suffix with CSV content; JSON will fail then CSV used
    p2 = tmp_path / "data2.dat"
    p2.write_text('c1,c2\n1,2\n', encoding="utf-8")
    rows2 = kv_import.read_any(p2)
    # Unknown suffix prefers JSON first; invalid JSON returns text wrapper
    assert rows2 and rows2[0]["value"] == 'c1,c2\n1,2\n'
