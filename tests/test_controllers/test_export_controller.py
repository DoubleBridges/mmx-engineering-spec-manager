import pytest

from mmx_engineering_spec_manager.controllers.export_controller import ExportController


class DummyDataManager:
    pass


class DummyExportTab:
    pass


def test_export_controller_set_active_project(qtbot):
    data_manager = DummyDataManager()
    export_tab = DummyExportTab()

    controller = ExportController(data_manager, export_tab)

    class Project:
        def __init__(self, number):
            self.number = number

    project = Project(number="101")

    # Call the slot to ensure it sets the internal state
    controller.set_active_project(project)

    # Verify internal state was set
    assert controller._active_project is project
