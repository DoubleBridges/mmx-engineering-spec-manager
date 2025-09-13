from mmx_engineering_spec_manager.views.attributes.attributes_tab import AttributesTab


auto_groups = {
    "Finishes": [
        {"Type": "Finish", "Name": "Lam B", "Tag": "PL9", "Description": "D"}
    ],
    "Hardware": [],
    "Sinks": [],
    "Appliances": [],
    "Uncategorized": [],
}


class FakeDMNew:
    def __init__(self):
        pass
    def get_callouts_for_project(self, pid):
        return auto_groups


class DummyProject:
    def __init__(self, id):
        self.id = id


def test_load_callouts_dm_lazy_creation(qtbot, monkeypatch):
    tab = AttributesTab()
    qtbot.addWidget(tab)

    # Force lazy DM creation path by ensuring _dm is None
    tab._dm = None
    # Monkeypatch DataManager constructor inside the attributes_tab module
    monkeypatch.setattr(
        "mmx_engineering_spec_manager.views.attributes.attributes_tab.DataManager",
        lambda: FakeDMNew(),
    )

    tab.set_active_project(DummyProject(123))
    tab.load_callouts_for_active_project()

    model = tab._callout_tables["Finishes"].model()
    assert model.rowCount() == 1
    assert model.item(0, 1).text() == "Lam B"
    assert model.item(0, 2).text() == "PL9"
