from mmx_engineering_spec_manager.views.attributes.attributes_tab import AttributesTab


def test_save_callouts_skips_incomplete_rows(qtbot, monkeypatch):
    tab = AttributesTab()
    qtbot.addWidget(tab)

    # One complete and one incomplete (missing Description) row
    tab._populate_callout_table(
        "Finishes",
        [
            {"Type": "Finish", "Name": "Lam A", "Tag": "PL1", "Description": "D"},
            {"Type": "Finish", "Name": "Lam B", "Tag": "PL2", "Description": ""},
        ],
    )

    class FakeDM:
        def __init__(self):
            self.called = False
            self.grouped = None
        def get_all_projects(self):
            return [type("P", (), {"id": 1, "number": "N", "name": "Proj"})()]
        def replace_callouts_for_project(self, pid, grouped):
            self.called = True
            self.grouped = grouped

    tab._dm = FakeDM()

    # Choose the only project
    monkeypatch.setattr(
        "mmx_engineering_spec_manager.views.attributes.attributes_tab.QInputDialog.getItem",
        lambda *args, **kwargs: ("N - Proj (ID 1)", True),
    )

    tab._on_save_callouts()

    assert tab._dm.called
    # Only the first complete row should be saved
    assert len(tab._dm.grouped["Finishes"]) == 1
