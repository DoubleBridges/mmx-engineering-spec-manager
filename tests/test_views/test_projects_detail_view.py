from unittest.mock import Mock

from PySide6.QtWidgets import QFormLayout, QTabWidget

from mmx_engineering_spec_manager.views.projects.projects_detail_view import ProjectsDetailView

def test_projects_detail_view_has_form_and_tabs(qtbot):
    """
    Test that the ProjectsDetailView has a QFormLayout and a QTabWidget.
    """
    projects_detail_view = ProjectsDetailView()
    qtbot.addWidget(projects_detail_view)

    # Assert that a QFormLayout exists
    form_layout = projects_detail_view.findChild(QFormLayout)
    assert form_layout is not None

    # Assert that a QTabWidget exists
    tab_widget = projects_detail_view.findChild(QTabWidget)
    assert tab_widget is not None

def test_projects_detail_view_displays_project_data(qtbot):
    """
    Test that the ProjectsDetailView correctly displays project data in the form layout.
    """
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

    projects_detail_view = ProjectsDetailView()
    qtbot.addWidget(projects_detail_view)

    mock_project = MockProject(
        number="101",
        name="Test Project",
        job_description="A complete project example."
    )

    projects_detail_view.display_project(mock_project)

    # Assert that the QFormLayout has the correct number of rows
    form_layout = projects_detail_view.findChild(QFormLayout)
    assert form_layout.rowCount() == 3

    # Assert that the labels and values are correct
    assert form_layout.itemAt(0, QFormLayout.ItemRole.LabelRole).widget().text() == "Number:"
    assert form_layout.itemAt(0, QFormLayout.ItemRole.FieldRole).widget().text() == "101"

    assert form_layout.itemAt(1, QFormLayout.ItemRole.LabelRole).widget().text() == "Name:"
    assert form_layout.itemAt(1, QFormLayout.ItemRole.FieldRole).widget().text() == "Test Project"

    assert form_layout.itemAt(2, QFormLayout.ItemRole.LabelRole).widget().text() == "Job Description:"
    assert form_layout.itemAt(2, QFormLayout.ItemRole.FieldRole).widget().text() == "A complete project example."

def test_projects_detail_view_displays_project_collections(qtbot):
    """
    Test that the ProjectsDetailView correctly displays project collections in the tab widget.
    """

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

    projects_detail_view = ProjectsDetailView()
    qtbot.addWidget(projects_detail_view)

    # Create a mock project object with empty collections
    mock_project = MockProject(
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

    projects_detail_view.display_project(mock_project)

    # Assert that the QTabWidget has the correct number of tabs
    tab_widget = projects_detail_view.findChild(QTabWidget)
    assert tab_widget.count() == 7

    # Assert that the tabs have the correct names
    assert tab_widget.tabText(0) == "Locations"
    assert tab_widget.tabText(1) == "Products"
    assert tab_widget.tabText(2) == "Walls"
    assert tab_widget.tabText(3) == "Custom Fields"
    assert tab_widget.tabText(4) == "Specification Groups"
    assert tab_widget.tabText(5) == "Global Prompts"
    assert tab_widget.tabText(6) == "Wizard Prompts"