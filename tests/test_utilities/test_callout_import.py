from pathlib import Path
import json

def test_categorize_by_tag_and_grouping(tmp_path):
    from mmx_engineering_spec_manager.utilities import callout_import as ci

    # Direct categorize_by_tag checks
    assert ci.categorize_by_tag("PL12") == ci.TYPE_FINISH
    assert ci.categorize_by_tag("pt99") == ci.TYPE_FINISH
    assert ci.categorize_by_tag("HW01") == ci.TYPE_HARDWARE
    assert ci.categorize_by_tag("bk77") == ci.TYPE_HARDWARE
    assert ci.categorize_by_tag("SK1") == ci.TYPE_SINK
    assert ci.categorize_by_tag("AP2") == ci.TYPE_APPLIANCE
    assert ci.categorize_by_tag("") == ci.TYPE_UNCATEGORIZED
    assert ci.categorize_by_tag("X") == ci.TYPE_UNCATEGORIZED

    # Grouping via DTOs
    dtos = [
        ci._mk_dto("Laminate A", "PL1", "Desc"),
        ci._mk_dto("Handle", "HW1", "Desc"),
        ci._mk_dto("Sink", "SK1", "Desc"),
        ci._mk_dto("Microwave", "AP1", "Desc"),
        ci._mk_dto("Unknown", "ZZ1", "Desc"),
    ]
    grouped = ci.group_callouts(dtos)
    assert len(grouped["Finishes"]) == 1
    assert len(grouped["Hardware"]) == 1
    assert len(grouped["Sinks"]) == 1
    assert len(grouped["Appliances"]) == 1
    assert len(grouped["Uncategorized"]) == 1


def test_parse_csv_callouts_and_dispatch(tmp_path):
    from mmx_engineering_spec_manager.utilities import callout_import as ci

    csv_text = """Name,Tag,Description\nLam A,PL1,Finish one\n,,\nHandle,HW2,Hardware two\nBad, , Row\n\n"""
    p = tmp_path / "callouts.csv"
    p.write_text(csv_text, encoding="utf-8")

    dtos = ci.parse_csv_callouts(p)
    # Should skip header, blank, and rows with missing required fields
    assert [(d.name, d.tag, d.description, d.type) for d in dtos] == [
        ("Lam A", "PL1", "Finish one", ci.TYPE_FINISH),
        ("Handle", "HW2", "Hardware two", ci.TYPE_HARDWARE),
    ]

    # read_callouts dispatch
    dtos2 = ci.read_callouts("csv", p)
    assert [(d.name, d.tag) for d in dtos2] == [("Lam A", "PL1"), ("Handle", "HW2")]


def test_parse_json_callouts_and_dispatch(tmp_path):
    from mmx_engineering_spec_manager.utilities import callout_import as ci

    data = [
        ["Lam A", "PL1", "Finish one"],
        ["", "HW3", "Missing name"],
        ["Handle", "", "Missing tag"],
        ["Widget", "ZZ9", "Unk"],  # Uncategorized
        ["Sink", "SK5", "Basin"],
        {"bad": "type"},
        ["Microwave", "AP1", ""],
    ]
    p = tmp_path / "callouts.json"
    p.write_text(json.dumps(data), encoding="utf-8")

    dtos = ci.parse_json_callouts(p)
    assert [(d.name, d.tag, d.type) for d in dtos] == [
        ("Lam A", "PL1", ci.TYPE_FINISH),
        ("Widget", "ZZ9", ci.TYPE_UNCATEGORIZED),
        ("Sink", "SK5", ci.TYPE_SINK),
    ]

    dtos2 = ci.read_callouts("json", p)
    assert [(d.name, d.tag) for d in dtos2] == [("Lam A", "PL1"), ("Widget", "ZZ9"), ("Sink", "SK5")]
