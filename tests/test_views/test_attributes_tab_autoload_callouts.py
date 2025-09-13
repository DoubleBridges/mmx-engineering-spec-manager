from mmx_engineering_spec_manager.views.attributes.attributes_tab import AttributesTab


auto_groups = {
    "Finishes": [
        {"Type": "Finish", "Name": "Lam A", "Tag": "PL1", "Description": "Desc"}
    ],
    "Hardware": [],
    "Sinks": [],
    "Appliances": [],
    "Uncategorized": [],
}


class FakeDM:
    def __init__(self, groups):
        self._groups = groups
    def get_callouts_for_project(self, pid):
        return self._groups


class DummyProject:
    def __init__(self, id):
        self.id = id


def test_load_callouts_for_active_project_populates_tables(qtbot):
    tab = AttributesTab()
    qtbot.addWidget(tab)

    # Inject fake data manager and active project
    tab._dm = FakeDM(auto_groups)
    tab.set_active_project(DummyProject(1))

    tab.load_callouts_for_active_project()

    model = tab._callout_tables["Finishes"].model()
    assert model.rowCount() == 1
    assert model.item(0, 1).text() == "Lam A"
    assert model.item(0, 2).text() == "PL1"
