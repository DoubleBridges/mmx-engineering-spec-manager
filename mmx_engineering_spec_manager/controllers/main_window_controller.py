from PySide6.QtCore import QObject

from .export_controller import ExportController
from .projects_controller import ProjectsController
from .workspace_controller import WorkspaceController


class MainWindowController(QObject):
    def __init__(self, main_window, data_manager):
        super().__init__(main_window)
        self.main_window = main_window
        self.data_manager = data_manager
        self._projects_controller = None

        self.main_window.window_ready_signal.connect(self.initialize)

    def initialize(self):
        self._projects_controller = ProjectsController(
            data_manager=self.data_manager,
            projects_tab=self.main_window.projects_tab,
            projects_detail_view=self.main_window.projects_detail_view
        )

        self._workspace_controller = WorkspaceController(
            data_manager=self.data_manager,
            workspace_tab=self.main_window.workspace_tab
        )

        self._export_controller = ExportController(
            data_manager=self.data_manager,
            export_tab=self.main_window.export_tab
        )

        # Connect the controllers
        self._projects_controller.project_opened_signal.connect(
            self._workspace_controller.set_active_project
        )

        self._projects_controller.project_opened_signal.connect(
            self._export_controller.set_active_project
        )