from pathlib import Path

from mmx_engineering_spec_manager.views.attributes.attributes_tab import AttributesTab


def test_load_file_clicked_generic_json_fallback(qtbot, monkeypatch, tmp_path):
    tab = AttributesTab()
    qtbot.addWidget(tab)

    # Create an empty JSON file path (content irrelevant since we'll monkeypatch loaders)
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
    # Make generic kv_import return one row
    monkeypatch.setattr(
        "mmx_engineering_spec_manager.views.attributes.attributes_tab.kv_import.read_any",
        lambda path: [{"a": 1, "b": 2}],
    )

    tab._on_load_file_clicked()

    # Table model should be populated via generic loader
    model = tab.table.model()
    assert model is not None
    assert model.rowCount() == 1
