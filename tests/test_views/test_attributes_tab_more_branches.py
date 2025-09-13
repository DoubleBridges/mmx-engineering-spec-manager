from PySide6.QtWidgets import QLineEdit, QStyleOptionViewItem

from mmx_engineering_spec_manager.views.attributes.attributes_tab import AttributesTab


def test_populate_callout_table_unknown_tab_returns(qtbot):
    tab = AttributesTab()
    qtbot.addWidget(tab)
    # Unknown tab should not raise
    tab._populate_callout_table("NotATab", [{"Type": "Finish", "Name": "X", "Tag": "PL1", "Description": "D"}])


def test_delegate_else_branches(qtbot):
    tab = AttributesTab()
    qtbot.addWidget(tab)

    # Put a row into Uncategorized
    tab._populate_callout_table(
        "Uncategorized",
        [{"Type": "Uncategorized", "Name": "X", "Tag": "ZZ1", "Description": "D"}],
    )
    view = tab._callout_tables["Uncategorized"]
    model = view.model()

    # Use a non-combo editor by addressing a non-Type column (e.g., column 1)
    idx = model.index(0, 1)
    option = QStyleOptionViewItem()
    editor = tab._uncat_delegate.createEditor(view, option, idx)
    # For non-Type columns PySide typically returns the base editor; just ensure setEditorData/setModelData 'else' paths run
    tab._uncat_delegate.setEditorData(editor, idx)
    tab._uncat_delegate.setModelData(editor, model, idx)


def test_save_callouts_project_selection_cancel(qtbot, monkeypatch):
    tab = AttributesTab()
    qtbot.addWidget(tab)

    class FakeDM3:
        def get_all_projects(self):
            return [type("P", (), {"id": 1, "number": "N", "name": "Proj"})()]
        def replace_callouts_for_project(self, pid, grouped):
            raise AssertionError("Should not be called when selection canceled")

    tab._dm = FakeDM3()

    # Cancel selection
    monkeypatch.setattr(
        "mmx_engineering_spec_manager.views.attributes.attributes_tab.QInputDialog.getItem",
        lambda *args, **kwargs: ("ignored", False),
    )

    tab._on_save_callouts()
