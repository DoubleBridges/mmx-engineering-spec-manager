from mmx_engineering_spec_manager.views.workspace.workspace_tab import WorkspaceTab


def test_workspace_tab_uses_wall_dimensions_when_present(qtbot):
    tab = WorkspaceTab()
    qtbot.addWidget(tab)

    class Wall:
        def __init__(self):
            self.width = 150.0
            self.thicknesses = 5.0
            self.height = 90.0

    class Proj:
        def __init__(self):
            self.name = "Proj"
            self.number = "P-1"
            self.walls = [Wall()]

    tab.display_project_data(Proj())

    # verify that internal views are set with provided dimensions
    assert abs(tab.plan_view.wall_length() - 150.0) < 1e-6
    assert abs(tab.elevation_view.wall_length() - 150.0) < 1e-6
    assert abs(tab.elevation_view.wall_height() - 90.0) < 1e-6
