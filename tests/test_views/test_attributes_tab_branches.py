import json
from PySide6.QtWidgets import QComboBox

from mmx_engineering_spec_manager.views.attributes.attributes_tab import AttributesTab


def test_load_file_cancel_and_unknown_type(qtbot, monkeypatch, tmp_path):
    tab = AttributesTab()
    qtbot.addWidget(tab)

    # Cancel type selection
    monkeypatch.setattr(
        "mmx_engineering_spec_manager.views.attributes.attributes_tab.QInputDialog.getItem",
        lambda *args, **kwargs: ("CSV", False),
    )
    tab._on_load_file_clicked()  # Should return early without error

    # Choose JSON but cancel file selection
    json_path = tmp_path / "callouts.json"
    json_path.write_text(json.dumps({"not": "a list"}), encoding="utf-8")
    monkeypatch.setattr(
        "mmx_engineering_spec_manager.views.attributes.attributes_tab.QInputDialog.getItem",
        lambda *args, **kwargs: ("JSON", True),
    )
    monkeypatch.setattr(
        "mmx_engineering_spec_manager.views.attributes.attributes_tab.QFileDialog.getOpenFileName",
        lambda *args, **kwargs: ("", ""),
    )
    tab._on_load_file_clicked()


def test_save_callouts_no_projects_lazy_dm(qtbot, monkeypatch):
    tab = AttributesTab()
    qtbot.addWidget(tab)

    class FakeDM2:
        def get_all_projects(self):
            return []

    # Force lazy creation path then override with our fake
    tab._dm = None
    monkeypatch.setattr(
        "mmx_engineering_spec_manager.views.attributes.attributes_tab.DataManager",
        lambda: FakeDM2(),
    )

    tab._on_save_callouts()  # Should return early without error


def test_uncategorized_type_delegate_end_to_end(qtbot):
    tab = AttributesTab()
    qtbot.addWidget(tab)

    # Add one row in Uncategorized and edit Type via delegate
    tab._populate_callout_table(
        "Uncategorized",
        [{"Type": "Uncategorized", "Name": "X", "Tag": "ZZ1", "Description": "D"}],
    )

    view = tab._callout_tables["Uncategorized"]
    model = view.model()

    # Create editor for Type column (0)
    idx = model.index(0, 0)
    editor = tab._uncat_delegate.createEditor(view, None, idx)
    assert isinstance(editor, QComboBox)

    # Set editor data and then change selection
    tab._uncat_delegate.setEditorData(editor, idx)
    # Change to Hardware
    i = editor.findText("Hardware")
    editor.setCurrentIndex(i)
    tab._uncat_delegate.setModelData(editor, model, idx)

    # Verify model updated
    assert model.item(0, 0).text() == "Hardware"
