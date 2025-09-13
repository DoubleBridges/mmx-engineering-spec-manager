def test_read_callouts_unknown_and_json_non_list(tmp_path):
    from mmx_engineering_spec_manager.utilities import callout_import as ci

    # Unknown file type returns []
    assert ci.read_callouts("xml", "dummy.txt") == []

    # JSON that isn't a list returns []
    p = tmp_path / "bad.json"
    p.write_text("{\"not\": \"a list\"}", encoding="utf-8")
    assert ci.parse_json_callouts(p) == []
