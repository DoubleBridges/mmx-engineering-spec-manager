from PySide6.QtCore import QObject

from .export_controller import ExportController
from .projects_controller import ProjectsController
from .workspace_controller import WorkspaceController


class MainWindowController(QObject):
    def __init__(self, main_window, data_manager, view_model=None):
        super().__init__(main_window)
        self.main_window = main_window
        self.data_manager = data_manager
        self.view_model = view_model
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

        # Connect the controllers (legacy direct wiring)
        self._projects_controller.project_opened_signal.connect(
            self._workspace_controller.set_active_project
        )

        self._projects_controller.project_opened_signal.connect(
            self._export_controller.set_active_project
        )

        # Wire MainWindow refresh (View->Refresh or F5) to reload projects
        try:
            self.main_window.refresh_requested.connect(self._projects_controller.load_projects)
        except Exception:
            pass

        # Transitional: if a ViewModel is provided, bridge its events to controllers
        try:
            if self.view_model is not None:
                self.view_model.project_opened.subscribe(self._workspace_controller.set_active_project)
                self.view_model.project_opened.subscribe(self._export_controller.set_active_project)
                self.view_model.refresh_requested.subscribe(lambda: self._projects_controller.load_projects())
        except Exception:
            # Do not fail the app if VM bridging fails
            pass