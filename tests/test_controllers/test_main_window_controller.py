from PySide6.QtCore import QObject, Signal

from mmx_engineering_spec_manager.controllers.main_window_controller import MainWindowController
from mmx_engineering_spec_manager.db_models.project import Project


class MockProjectsTab(QObject):
    load_projects_signal = Signal()
    open_project_signal = Signal(object)

class MockMainWindow(QObject):
    def __init__(self, projects_tab):
        super().__init__()
        self.projects_tab = projects_tab

def test_controller_loads_projects_on_signal(mocker):
    """
    Test that the controller's load_projects method is called when the signal is emitted.
    """
    # Create a mock controller and a mock ProjectsTab
    mock_projects_tab = MockProjectsTab()
    mock_controller = mocker.Mock()

    # Call the method that connects the signal to the slot
    MainWindowController.connect_projects_tab(mock_controller, mock_projects_tab)

    # Simulate the signal being emitted
    mock_projects_tab.load_projects_signal.emit()

    # Assert that the controller's load_projects method was called
    mock_controller.load_projects.assert_called_once()


def test_controller_loads_projects_from_data_manager(mocker):
    """
    Test that the controller's load_projects method calls the DataManager.
    """
    # Create mock DataManager
    mock_data_manager = mocker.Mock()
    mock_data_manager.get_all_projects.return_value = []

    # Create a mock main window
    mock_main_window = mocker.Mock()

    # Create a new controller instance with the mocked DataManager
    controller = MainWindowController(
        main_window=mock_main_window,
        data_manager=mock_data_manager,
    )

    # Call the method we want to test
    controller.load_projects()

    # Assert that the DataManager's method was called
    mock_data_manager.get_all_projects.assert_called_once()


def test_controller_displays_projects_in_view(mocker):
    """
    Test that the controller's load_projects method updates the view.
    """
    # Create mock DataManager
    mock_project_1 = Project(number="101", name="Test Project 1")
    mock_project_2 = Project(number="102", name="Test Project 2")
    mock_data_manager = mocker.Mock()
    mock_data_manager.get_all_projects.return_value = [mock_project_1, mock_project_2]

    # Create mock ProjectsTab
    mock_projects_tab = mocker.Mock()

    # Create a mock main window
    mock_main_window = mocker.Mock()
    mock_main_window.projects_tab = mock_projects_tab
    mock_main_window.central_widget = mock_projects_tab

    # Create a new controller instance with the mocked DataManager
    controller = MainWindowController(
        main_window=mock_main_window,
        data_manager=mock_data_manager
    )

    # Call the method we want to test
    controller.load_projects()

    # Assert that the ProjectsTab's display_projects method was called with the projects
    mock_projects_tab.display_projects.assert_called_once_with([mock_project_1, mock_project_2])

def test_controller_opens_project_on_signal(mocker):
    """
    Test that the controller's open_project method is called when the signal is emitted.
    """
    # Create a mock controller and a mock ProjectsTab
    mock_projects_tab = MockProjectsTab()
    mock_main_window = MockMainWindow(projects_tab=mock_projects_tab)
    mock_controller = mocker.Mock()

    # Create a mock project object to be passed with the signal
    mock_project = Project(
        number="101",
        name="Test Project",
        job_description="A complete project example."
    )

    # Call the method that connects the signal to the slot
    MainWindowController.connect_projects_tab(mock_controller, mock_projects_tab)

    # Simulate the signal being emitted with the mock project
    mock_projects_tab.open_project_signal.emit(mock_project)

    # Assert that the controller's open_project method was called
    mock_controller.open_project.assert_called_once_with(mock_project)