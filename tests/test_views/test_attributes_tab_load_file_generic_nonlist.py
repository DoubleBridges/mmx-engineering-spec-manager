from mmx_engineering_spec_manager.views.attributes.attributes_tab import AttributesTab


def test_load_file_clicked_generic_json_fallback_nonlist_rows(qtbot, monkeypatch, tmp_path):
    tab = AttributesTab()
    qtbot.addWidget(tab)

    # Create an empty JSON file path
    p = tmp_path / "dummy.json"
    p.write_text("{}", encoding="utf-8")

    # Force JSON path via dialog selection
    monkeypatch.setattr(
        "mmx_engineering_spec_manager.views.attributes.attributes_tab.QInputDialog.getItem",
        lambda *args, **kwargs: ("JSON", True),
    )
    monkeypatch.setattr(
        "mmx_engineering_spec_manager.views.attributes.attributes_tab.QFileDialog.getOpenFileName",
        lambda *args, **kwargs: (str(p), ""),
    )

    # Make callout parsing return nothing so it falls back to generic loader
    monkeypatch.setattr(
        "mmx_engineering_spec_manager.views.attributes.attributes_tab.callout_import.read_callouts",
        lambda file_type, path: [],
    )
    # Make generic kv_import return a non-list to trigger rows=[] branch
    monkeypatch.setattr(
        "mmx_engineering_spec_manager.views.attributes.attributes_tab.kv_import.read_any",
        lambda path: {"a": 1},
    )

    tab._on_load_file_clicked()

    assert tab.current_rows() == []
    assert tab.table.model() is not None
