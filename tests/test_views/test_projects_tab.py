import PySide6
import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel

from mmx_engineering_spec_manager.views.projects.projects_tab import ProjectsTab


@pytest.fixture
def mock_project():
    class MockProject:
        def __init__(self, number, name, job_description):
            self.number = number
            self.name = name
            self.job_description = job_description

    return MockProject(number="101", name="Project One", job_description="Description 1")

@pytest.fixture
def mock_projects():
    class MockProject:
        def __init__(self, number, name, job_description):
            self.number = number
            self.name = name
            self.job_description = job_description

    return [
        MockProject(number="101", name="Project One", job_description="Description 1"),
        MockProject(number="102", name="Project Two", job_description="Description 2")
    ]

def test_load_projects_button_emits_signal(qtbot):
    """
    Test that clicking the 'Load Projects' button emits a signal.
    """
    projects_tab = ProjectsTab()
    qtbot.addWidget(projects_tab)

    # Find the 'Load Projects' button
    load_button = projects_tab.load_button
    assert load_button is not None

    # Use qtbot to simulate a click and check for a signal
    with qtbot.waitSignal(projects_tab.load_projects_signal, timeout=1000):
        qtbot.mouseClick(load_button, PySide6.QtCore.Qt.LeftButton)

def test_projects_tab_displays_projects(qtbot, mock_projects):
    """
    Test that the ProjectsTab correctly populates the QTableView with projects.
    """
    projects_tab = ProjectsTab()
    qtbot.addWidget(projects_tab)

    # Call the display_projects method
    projects_tab.display_projects(mock_projects)

    # Assert that the QStandardItemModel has the correct data
    table_model = projects_tab.projects_table.model()
    assert isinstance(table_model, QStandardItemModel)
    assert table_model.rowCount() == 2
    assert table_model.columnCount() == 3

    assert table_model.item(0, 0).text() == "101"
    assert table_model.item(0, 1).text() == "Project One"
    assert table_model.item(0, 2).text() == "Description 1"

    assert table_model.item(1, 0).text() == "102"
    assert table_model.item(1, 1).text() == "Project Two"
    assert table_model.item(1, 2).text() == "Description 2"

def test_projects_tab_double_click_opens_project(qtbot, mocker, mock_projects):
    """
    Test that double-clicking a project in the table emits a signal with the project object.
    """
    projects_tab = ProjectsTab()
    qtbot.addWidget(projects_tab)
    projects_tab.display_projects(mock_projects)

    index_to_click = projects_tab.projects_table.model().index(0, 0)

    mocker.patch.object(projects_tab, 'open_project_signal')

    projects_tab.on_project_double_clicked(index_to_click)

    projects_tab.open_project_signal.emit.assert_called_once_with(mock_projects[0])

def test_projects_tab_displays_project_details(qtbot, mock_project):
    """
    Test that the ProjectsTab's display_project_details method is called with the correct project object.
    """
    projects_tab = ProjectsTab()
    qtbot.addWidget(projects_tab)

    projects_tab.display_project_details(mock_project)

    # Assert that the display_project_details method was called with the correct project object
    assert projects_tab.current_project == mock_project