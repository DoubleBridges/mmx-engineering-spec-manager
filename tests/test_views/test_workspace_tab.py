import pytest
from PySide6.QtGui import QStandardItemModel
from PySide6.QtWidgets import QTabWidget, QWidget, QTreeView
from mmx_engineering_spec_manager.views.main_window import MainWindow
from mmx_engineering_spec_manager.views.workspace.workspace_tab import WorkspaceTab

def test_main_window_has_workspace_tab(qtbot):
    """
    Test that the main window contains a QTabWidget with a 'Workspace' tab.
    """
    main_window = MainWindow()
    qtbot.addWidget(main_window)

    # Find the QTabWidget
    tab_widget = main_window.findChild(QTabWidget)
    assert tab_widget is not None

    # Check that the 'Workspace' tab exists
    workspace_tab = None
    for i in range(tab_widget.count()):
        if tab_widget.tabText(i) == "Workspace":
            workspace_tab = tab_widget.widget(i)
            break

    assert workspace_tab is not None
    assert isinstance(workspace_tab, WorkspaceTab)


def test_workspace_tab_has_tree_view(qtbot):
    """
    Test that the WorkspaceTab has a QTreeView.
    """
    workspace_tab = WorkspaceTab()
    qtbot.addWidget(workspace_tab)

    tree_view = workspace_tab.findChild(QTreeView)
    assert tree_view is not None


def test_workspace_tab_displays_project_hierarchy(qtbot):
    """
    Test that the WorkspaceTab correctly populates a QTreeView with project data.
    """

    # Create a simple class to act as a Project model
    class MockProject:
        def __init__(self, name, locations=None):
            self.name = name
            self.locations = locations if locations else []

    class MockLocation:
        def __init__(self, name):
            self.name = name

    workspace_tab = WorkspaceTab()
    qtbot.addWidget(workspace_tab)

    mock_project = MockProject(
        name="Test Project",
        locations=[
            MockLocation(name="Kitchen"),
            MockLocation(name="Bathroom")
        ]
    )

    workspace_tab.display_project(mock_project)

    tree_model = workspace_tab.project_tree.model()
    assert isinstance(tree_model, QStandardItemModel)
    assert tree_model.rowCount() == 1
    assert tree_model.item(0).text() == "Test Project"

    assert tree_model.item(0).child(0).text() == "Kitchen"
    assert tree_model.item(0).child(1).text() == "Bathroom"