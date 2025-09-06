import pytest

from mmx_engineering_spec_manager.controllers.workspace_controller import WorkspaceController


class DummyDataManager:
    pass


class DummyWorkspaceTab:
    def __init__(self):
        self.calls = []

    def display_project_data(self, project):
        self.calls.append(project)


def test_workspace_controller_set_active_project_calls_view(qtbot):
    data_manager = DummyDataManager()
    workspace_tab = DummyWorkspaceTab()

    controller = WorkspaceController(data_manager, workspace_tab)

    class Project:
        def __init__(self, name):
            self.name = name

    project = Project(name="Proj A")

    controller.set_active_project(project)

    assert workspace_tab.calls and workspace_tab.calls[0] is project
