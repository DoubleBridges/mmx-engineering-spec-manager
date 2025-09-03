from PySide6.QtCore import QObject, Signal

from mmx_engineering_spec_manager.controllers.main_window_controller import MainWindowController


class MockProjectsDetailView(QObject):
    pass


class MockProjectsTab(QObject):
    pass


class MockWorkspaceTab(QObject):
    pass

class MockExportTab(QObject):
    pass

class MockMainWindow(QObject):
    window_ready_signal = Signal()

    def __init__(self):
        super().__init__()
        self.projects_tab = MockProjectsTab()
        self.projects_detail_view = MockProjectsDetailView()
        self.workspace_tab = MockWorkspaceTab()
        self.export_tab = MockExportTab()


def test_main_controller_initializes_controllers(mocker):
    """
    Test that MainWindowController initializes its child controllers on window_ready_signal.
    """
    mock_main_window = MockMainWindow()
    mock_data_manager = mocker.Mock()

    # Patch the controller classes in the context of the main_window_controller module
    mock_projects_controller_class = mocker.patch(
        'mmx_engineering_spec_manager.controllers.main_window_controller.ProjectsController'
    )
    mock_workspace_controller_class = mocker.patch(
        'mmx_engineering_spec_manager.controllers.main_window_controller.WorkspaceController'
    )

    mock_export_controller_class = mocker.patch(
        'mmx_engineering_spec_manager.controllers.main_window_controller.ExportController'
    )

    # Create the main controller
    controller = MainWindowController(
        main_window=mock_main_window,
        data_manager=mock_data_manager
    )

    # Simulate the window ready signal
    mock_main_window.window_ready_signal.emit()

    # Assert that ProjectsController was instantiated once with the correct arguments
    mock_projects_controller_class.assert_called_once_with(
        data_manager=mock_data_manager,
        projects_tab=mock_main_window.projects_tab,
        projects_detail_view=mock_main_window.projects_detail_view
    )

    # Assert that WorkspaceController was instantiated once
    mock_workspace_controller_class.assert_called_once_with(
        data_manager=mock_data_manager,
        workspace_tab=mock_main_window.workspace_tab
    )

    # Assert that ExportController was instantiated once
    mock_export_controller_class.assert_called_once_with(
        data_manager=mock_data_manager,
        export_tab=mock_main_window.export_tab
    )

    # Assert that the signal from projects_controller was connected to workspace_controller's slot
    mock_projects_controller_instance = mock_projects_controller_class.return_value
    mock_workspace_controller_instance = mock_workspace_controller_class.return_value
    mock_export_controller_instance = mock_export_controller_class.return_value

    mock_projects_controller_instance.project_opened_signal.connect.assert_any_call(
        mock_workspace_controller_instance.set_active_project
    )

    mock_projects_controller_instance.project_closed_signal.connect.asset_any_call(
        mock_workspace_controller_instance.set_active_project
    )