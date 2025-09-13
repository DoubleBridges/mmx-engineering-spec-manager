import json
from PySide6.QtWidgets import QTableView

from mmx_engineering_spec_manager.views.attributes.attributes_tab import AttributesTab


def test_populate_and_rows_round_trip(qtbot):
    tab = AttributesTab()
    qtbot.addWidget(tab)

    rows = [
        {"Type": "Finish", "Name": "Lam A", "Tag": "PL1", "Description": "D1"},
        {"Type": "Hardware", "Name": "Pull", "Tag": "HW3", "Description": "D2"},
    ]
    tab._populate_callout_table("Finishes", [rows[0]])
    tab._populate_callout_table("Hardware", [rows[1]])

    fin_rows = tab._rows_from_model(tab._callout_tables["Finishes"])  # type: ignore[attr-defined]
    hw_rows = tab._rows_from_model(tab._callout_tables["Hardware"])   # type: ignore[attr-defined]

    assert fin_rows == [rows[0]]
    assert hw_rows == [rows[1]]


def test_on_load_file_clicked_populates_tables_csv(qtbot, monkeypatch, tmp_path):
    tab = AttributesTab()
    qtbot.addWidget(tab)

    # Create a CSV file with header and two rows (one finish, one hardware)
    csv_text = "Name,Tag,Description\nLam A,PL1,Finish one\nPull,HW2,Hardware two\n"
    p = tmp_path / "callouts.csv"
    p.write_text(csv_text, encoding="utf-8")

    # Monkeypatch dialogs: choose CSV and return our path
    monkeypatch.setattr(
        "mmx_engineering_spec_manager.views.attributes.attributes_tab.QInputDialog.getItem",
        lambda *args, **kwargs: ("CSV", True),
    )
    monkeypatch.setattr(
        "mmx_engineering_spec_manager.views.attributes.attributes_tab.QFileDialog.getOpenFileName",
        lambda *args, **kwargs: (str(p), ""),
    )

    tab._on_load_file_clicked()

    # Verify tables populated
    fin_model = tab._callout_tables["Finishes"].model()  # type: ignore[attr-defined]
    hw_model = tab._callout_tables["Hardware"].model()   # type: ignore[attr-defined]
    assert fin_model.rowCount() == 1
    assert hw_model.rowCount() == 1


def test_on_save_callouts_groups_and_calls_dm(qtbot, monkeypatch):
    tab = AttributesTab()
    qtbot.addWidget(tab)

    # Pre-populate some rows including Uncategorized but with explicit type override
    tab._populate_callout_table(
        "Uncategorized",
        [
            {"Type": "Hardware", "Name": "Lam B", "Tag": "PL9", "Description": "D"},
            {"Type": "", "Name": "", "Tag": "", "Description": ""},  # ignored empty
        ],
    )
    tab._populate_callout_table(
        "Finishes",
        [
            {"Type": "Finish", "Name": "Lam A", "Tag": "PL1", "Description": "D"},
        ],
    )

    # Fake DataManager
    class FakeDM:
        def __init__(self):
            self.called = False
            self.args = None
        def get_all_projects(self):
            class P:
                id = 42
                number = "N"
                name = "Proj"
            return [P()]
        def replace_callouts_for_project(self, pid, grouped):
            self.called = True
            self.args = (pid, grouped)

    fake_dm = FakeDM()
    tab._dm = fake_dm  # inject fake

    # Choose project via dialog
    monkeypatch.setattr(
        "mmx_engineering_spec_manager.views.attributes.attributes_tab.QInputDialog.getItem",
        lambda *args, **kwargs: ("N - Proj (ID 42)", True),
    )

    tab._on_save_callouts()

    assert fake_dm.called
    pid, grouped = fake_dm.args
    assert pid == 42
    # Should have 1 finish and 1 hardware; Uncategorized not persisted
    assert len(grouped["Finishes"]) == 1
    assert len(grouped["Hardware"]) == 1
    assert len(grouped["Uncategorized"]) == 0
