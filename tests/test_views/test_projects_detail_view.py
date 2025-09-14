import PySide6
import pytest
from PySide6.QtWidgets import QTreeView
from PySide6.QtGui import QStandardItemModel

from mmx_engineering_spec_manager.views.projects.projects_detail_view import ProjectsDetailView


def _find_child_by_text(parent_item, text):
    for r in range(parent_item.rowCount()):
        child = parent_item.child(r, 0)
        if child and child.text() == text:
            return child
    return None


@pytest.fixture
def mock_project_data():
    class MockProject:
        def __init__(self, number, name, job_description, **collections):
            self.number = number
            self.name = name
            self.job_description = job_description
            self.locations = collections.get("locations", [])
            self.products = collections.get("products", [])
            self.walls = collections.get("walls", [])
            self.custom_fields = collections.get("custom_fields", [])
            self.specification_groups = collections.get("specification_groups", [])
            self.global_prompts = collections.get("global_prompts", [])
            self.wizard_prompts = collections.get("wizard_prompts", [])

    return MockProject(
        number="101",
        name="Test Project",
        job_description="A complete project example.",
        locations=["mock_location"],
        products=["mock_product"],
        walls=["mock_wall"],
        custom_fields=["mock_cf"],
        specification_groups=["mock_spec_group"],
        global_prompts=["mock_gp"],
        wizard_prompts=["mock_wp"]
    )

def test_projects_detail_view_has_tree_view(qtbot):
    """
    ProjectsDetailView should present a QTreeView-based layout now.
    """
    view = ProjectsDetailView()
    qtbot.addWidget(view)

    tree = view.findChild(QTreeView)
    assert tree is not None

def test_projects_detail_view_displays_project_data(qtbot, mock_project_data):
    """
    Test that the ProjectsDetailView correctly displays project data in the tree view under Properties.
    """

    view = ProjectsDetailView()
    qtbot.addWidget(view)

    view.display_project(mock_project_data)

    model = view.tree_view.model()
    assert isinstance(model, QStandardItemModel)

    root = model.item(0, 0)
    assert root.text() == "Project"

    props = _find_child_by_text(root, "Properties")
    assert props is not None

    # Build a dict of property -> value from the Properties node children
    kv = {}
    for r in range(props.rowCount()):
        k = props.child(r, 0).text()
        v = props.child(r, 1).text()
        kv[k] = v

    assert kv.get("Number") == "101"
    assert kv.get("Name") == "Test Project"
    assert kv.get("Job Description") == "A complete project example."

def test_projects_detail_view_displays_project_collections(qtbot, mock_project_data):
    """
    The tree should include collection groups as children of the root: Locations, Walls, Custom Fields,
    Specification Groups, Global Prompts, Wizard Prompts (when present). Products are nested under Locations.
    """

    view = ProjectsDetailView()
    qtbot.addWidget(view)

    view.display_project(mock_project_data)

    model = view.tree_view.model()
    root = model.item(0, 0)
    child_names = {root.child(r, 0).text() for r in range(root.rowCount())}

    assert "Properties" in child_names
    assert "Locations" in child_names
    assert "Walls" in child_names
    assert "Custom Fields" in child_names
    assert "Specification Groups" in child_names
    assert "Global Prompts" in child_names
    assert "Wizard Prompts" in child_names

def test_projects_detail_view_properties_auto_expanded(qtbot, mock_project_data):
    """
    The Properties group should be auto-expanded when a project is displayed.
    """
    view = ProjectsDetailView()
    qtbot.addWidget(view)

    view.display_project(mock_project_data)

    model = view.tree_view.model()
    root_index = model.index(0, 0)
    props_index = root_index.child(0, 0)

    assert view.tree_view.isExpanded(root_index)
    assert view.tree_view.isExpanded(props_index)

def test_save_button_emits_signal(qtbot, mock_project_data):
    """
    Test that clicking the 'Save' button emits a signal with the updated project data.
    """
    projects_detail_view = ProjectsDetailView()
    qtbot.addWidget(projects_detail_view)

    projects_detail_view.display_project(mock_project_data)

    # Find the save button
    save_button = projects_detail_view.save_button
    assert save_button is not None
    assert save_button.text() == "Save"

    # Use qtbot to simulate a click and check for a signal
    with qtbot.waitSignal(projects_detail_view.save_button_clicked_signal, timeout=1000) as blocker:
        qtbot.mouseClick(save_button, PySide6.QtCore.Qt.LeftButton)

    # The expected data should be a dictionary from the form fields
    expected_data = {
        "number": "101",
        "name": "Test Project",
        "job_description": "A complete project example."
    }

    # Assert that the signal was emitted with the correct dictionary
    assert blocker.args[0] == expected_data


def test_projects_detail_view_updates_on_redisplay(qtbot, mock_project_data):
    view = ProjectsDetailView()
    qtbot.addWidget(view)
    # first display
    view.display_project(mock_project_data)

    # second display with different data
    new_project = type(mock_project_data)(
        number="202",
        name="Another",
        job_description="Second",
        locations=[], products=[], walls=[], custom_fields=[], specification_groups=[], global_prompts=[], wizard_prompts=[]
    )
    view.display_project(new_project)

    model = view.tree_view.model()
    root = model.item(0, 0)
    props = _find_child_by_text(root, "Properties")
    kv = {props.child(r, 0).text(): props.child(r, 1).text() for r in range(props.rowCount())}
    assert kv.get("Number") == "202"
