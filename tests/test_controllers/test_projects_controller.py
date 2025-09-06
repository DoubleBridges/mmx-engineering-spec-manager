from PySide6.QtCore import QObject, Signal

from mmx_engineering_spec_manager.controllers.projects_controller import ProjectsController
from mmx_engineering_spec_manager.db_models.project import Project


class MockProjectsDetailView(QObject):
    save_button_clicked_signal = Signal(dict)

    def display_project(self, project):
        pass


class MockProjectsTab(QObject):
    open_project_signal = Signal(object)

    def display_projects(self, projects):
        pass


def test_controller_loads_projects_on_init(mocker):
    """
    Test that the controller loads projects when it is initialized.
    """
    mock_data_manager = mocker.Mock()
    mock_data_manager.get_all_projects.return_value = []
    mock_projects_tab = MockProjectsTab()
    mock_projects_detail_view = MockProjectsDetailView()

    mocker.spy(mock_projects_tab, 'display_projects')

    # The controller loads projects in its __init__ method
    controller = ProjectsController(
        data_manager=mock_data_manager,
        projects_tab=mock_projects_tab,
        projects_detail_view=mock_projects_detail_view
    )

    mock_data_manager.get_all_projects.assert_called_once()
    mock_projects_tab.display_projects.assert_called_once_with([])


# Removed obsolete reload signal test as UI button/signal were removed


def test_controller_displays_projects_in_view(mocker):
    """
    Test that the controller's load_projects method updates the view.
    """
    mock_project_1 = Project(number="101", name="Test Project 1")
    mock_project_2 = Project(number="102", name="Test Project 2")
    mock_data_manager = mocker.Mock()
    mock_data_manager.get_all_projects.return_value = [mock_project_1, mock_project_2]

    mock_projects_tab = mocker.Mock()
    mock_projects_detail_view = MockProjectsDetailView()

    controller = ProjectsController(
        data_manager=mock_data_manager,
        projects_tab=mock_projects_tab,
        projects_detail_view=mock_projects_detail_view
    )

    # Call the method we want to test (it's also called on init, so we check the latest call)
    controller.load_projects()

    # Assert that the ProjectsTab's display_projects method was called with the projects
    mock_projects_tab.display_projects.assert_called_with([mock_project_1, mock_project_2])


def test_controller_opens_project_on_signal(mocker):
    """
    Test that the controller's open_project method is called when the signal is emitted.
    """
    mock_data_manager = mocker.Mock()
    mock_projects_tab = MockProjectsTab()
    mock_projects_detail_view = MockProjectsDetailView()

    controller = ProjectsController(
        data_manager=mock_data_manager,
        projects_tab=mock_projects_tab,
        projects_detail_view=mock_projects_detail_view
    )
    mocker.spy(controller, 'open_project')

    mock_project = Project(number="101", name="Test Project")

    # Simulate the signal being emitted with the mock project
    mock_projects_tab.open_project_signal.emit(mock_project)

    # Assert that the controller's open_project method was called
    controller.open_project.assert_called_once_with(mock_project)


def test_controller_saves_project_on_signal(mocker):
    """
    Test that the controller's save_project method is called when the signal is emitted.
    """
    mock_data_manager = mocker.Mock()
    mock_projects_tab = MockProjectsTab()
    mock_projects_detail_view = MockProjectsDetailView()

    controller = ProjectsController(
        data_manager=mock_data_manager,
        projects_tab=mock_projects_tab,
        projects_detail_view=mock_projects_detail_view
    )
    mocker.spy(controller, 'save_project')

    mock_project_data = {"name": "Test"}

    # Simulate the signal being emitted with the mock project data
    mock_projects_detail_view.save_button_clicked_signal.emit(mock_project_data)

    # Assert that the controller's save_project method was called
    controller.save_project.assert_called_once_with(mock_project_data)


def test_controller_saves_project_with_data_manager(mocker):
    """
    Test that the controller's save_project method calls the DataManager.
    """
    mock_data_manager = mocker.Mock()
    mock_projects_tab = MockProjectsTab()
    mock_projects_detail_view = MockProjectsDetailView()

    controller = ProjectsController(
        data_manager=mock_data_manager,
        projects_tab=mock_projects_tab,
        projects_detail_view=mock_projects_detail_view
    )

    mock_project_data = {"name": "Updated Project Name"}

    # Call the method we want to test
    controller.save_project(mock_project_data)

    # Assert that the DataManager's method was called with the correct data
    mock_data_manager.save_project.assert_called_once_with(mock_project_data)
    # The new logic also reloads projects after saving
    assert mock_data_manager.get_all_projects.call_count == 2  # once on init, once after save


def test_controller_displays_opened_project_details(mocker):
    """
    Test that the controller's open_project method displays the project details.
    """
    mock_project = Project(id=1, number="101", name="Test Project")
    mock_data_manager = mocker.Mock()
    mock_data_manager.get_project_by_id.return_value = mock_project
    mock_projects_tab = MockProjectsTab()
    mock_projects_detail_view = mocker.Mock()

    controller = ProjectsController(
        data_manager=mock_data_manager,
        projects_tab=mock_projects_tab,
        projects_detail_view=mock_projects_detail_view
    )

    # Call the method we want to test
    controller.open_project(mock_project)

    # Assert that the DataManager was called
    mock_data_manager.get_project_by_id.assert_called_once_with(mock_project.id)
    # Assert that the ProjectsDetailView's display_project method was called
    mock_projects_detail_view.display_project.assert_called_once_with(mock_project)