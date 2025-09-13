import json
from pathlib import Path

from mmx_engineering_spec_manager.utilities.callout_import import parse_json_callouts


def test_parse_json_callouts_handles_non_list_and_short_rows(tmp_path):
    data = {
        "d": [
            {"not": "a list"},    # non-list item should be skipped
            ["ONLY_TWO", "C1"],     # len < 3 should be skipped
            ["HEADER", "", ""],    # not a known header; will be treated as data but has empty desc -> skipped
        ]
    }
    p = tmp_path / "callouts.json"
    p.write_text(json.dumps(data), encoding="utf-8")

    out = parse_json_callouts(str(p))
    # All entries should be skipped; result empty
    assert out == []
