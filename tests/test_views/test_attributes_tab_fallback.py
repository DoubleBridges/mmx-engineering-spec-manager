from mmx_engineering_spec_manager.views.attributes.attributes_tab import AttributesTab


def test_attributes_tab_handles_non_list_rows(qtbot, monkeypatch):
    tab = AttributesTab()
    qtbot.addWidget(tab)

    # Make kv_import.read_any return a non-list, triggering fallback to []
    import mmx_engineering_spec_manager.utilities.kv_import as kv
    monkeypatch.setattr(kv, 'read_any', lambda path: {"a": 1})

    tab.load_from_path("dummy.txt")

    assert tab.current_rows() == []
    assert tab.table.model() is not None
