from PySide6.QtCore import QObject

from .export_controller import ExportController
from .projects_controller import ProjectsController
from .workspace_controller import WorkspaceController


class MainWindowController(QObject):
    """DEPRECATED: Legacy controller kept during MVVM transition.

    New logic should live in ViewModels and Services. This controller now
    primarily instantiates sub-controllers for legacy Views and bridges
    ViewModel events to them via a thin adapter.
    """
    def __init__(self, main_window, data_manager, view_model=None):
        super().__init__(main_window)
        self.main_window = main_window
        self.data_manager = data_manager
        self.view_model = view_model
        self._projects_controller = None
        self._workspace_controller = None
        self._export_controller = None
        self._vm_bridge = None

        self.main_window.window_ready_signal.connect(self.initialize)

    def initialize(self):
        # Build a ProjectsViewModel and pass it to the controller (MVVM migration)
        try:
            from mmx_engineering_spec_manager.core.composition_root import build_projects_view_model
            projects_vm = build_projects_view_model(self.data_manager)
        except Exception:
            projects_vm = None
        self._projects_controller = ProjectsController(
            data_manager=self.data_manager,
            projects_tab=self.main_window.projects_tab,
            projects_detail_view=self.main_window.projects_detail_view,
            view_model=projects_vm,
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
                from .legacy_vm_bridge import ThinVMControllerBridge
                self._vm_bridge = ThinVMControllerBridge(
                    view_model=self.view_model,
                    projects_controller=self._projects_controller,
                    workspace_controller=self._workspace_controller,
                    export_controller=self._export_controller,
                )
        except Exception:
            # Do not fail the app if VM bridging fails
            self._vm_bridge = None
            pass