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

    workspace_tab.open_project_in_workspace(mock_project)

    tree_model = workspace_tab.project_tree.model()
    assert isinstance(tree_model, QStandardItemModel)
    assert tree_model.rowCount() == 1
    assert tree_model.item(0).text() == "Test Project"

    assert tree_model.item(0).child(0).text() == "Kitchen"
    assert tree_model.item(0).child(1).text() == "Bathroom"


def test_workspace_tab_displays_project_products(qtbot):
    """
    Test that the WorkspaceTab displays a QTreeView with project products.
    """

    class MockProject:
        def __init__(self, name, locations=None, walls=None, products=None):
            self.name = name
            self.locations = locations if locations else []
            self.walls = walls if walls else []
            self.products = products if products else []

    class MockLocation:
        def __init__(self, name, id):
            self.name = name
            self.id = id

    class MockWall:
        def __init__(self, link_id, location_id, id, products=None):
            self.link_id = link_id
            self.location_id = location_id
            self.id = id
            self.products = products if products else []

    class MockProduct:
        def __init__(self, name, wall_id):
            self.name = name
            self.wall_id = wall_id

    workspace_tab = WorkspaceTab()
    qtbot.addWidget(workspace_tab)

    mock_project = MockProject(
        name="Test Project",
        locations=[
            MockLocation(name="Kitchen", id=1),
        ],
        walls=[
            MockWall(link_id="wall_1", location_id=1, id=1)
        ],
        products=[
            MockProduct(name="product_1", wall_id=1),
            MockProduct(name="product_2", wall_id=1)
        ]
    )

    workspace_tab.open_project_in_workspace(mock_project)

    tree_model = workspace_tab.project_tree.model()

    # Check that the products exist under the correct wall
    kitchen_item = tree_model.item(0).child(0)
    wall_item = kitchen_item.child(0)

    assert wall_item.child(0).text() == "product_1"
    assert wall_item.child(1).text() == "product_2"