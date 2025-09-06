from PySide6.QtCore import QObject, Slot, Signal
from PySide6.QtWidgets import QMessageBox

from mmx_engineering_spec_manager.utilities.async_worker import run_in_thread
from mmx_engineering_spec_manager.utilities.logging_config import get_logger
from mmx_engineering_spec_manager.utilities.settings import get_settings


class ProjectsController(QObject):
    """
    Controller to manage the projects tab and project detail view.
    """
    project_opened_signal = Signal(object)

    def __init__(self, data_manager, projects_tab, projects_detail_view):
        super().__init__()
        self.data_manager = data_manager
        self.projects_tab = projects_tab
        self.projects_detail_view = projects_detail_view
        self._import_thread = None
        self._import_worker = None

        self._connect_signals()
        self.load_projects()

    def _connect_signals(self):
        self.projects_tab.load_projects_signal.connect(self.load_projects)
        self.projects_tab.open_project_signal.connect(self.open_project)
        self.projects_detail_view.save_button_clicked_signal.connect(self.save_project)
        # Wire import to async handler
        if hasattr(self.projects_tab, 'import_projects_signal'):
            self.projects_tab.import_projects_signal.connect(self.import_from_innergy)

    @Slot()
    def load_projects(self):
        """Loads all projects from the data manager and displays them in the projects tab."""
        projects = self.data_manager.get_all_projects()
        self.projects_tab.display_projects(projects)

    @Slot()
    def import_from_innergy(self):
        """Run Innergy sync in background and refresh project list when done."""
        logger = get_logger(__name__)
        # Pre-flight settings validation for user-friendly feedback
        s = get_settings()
        if not s.innergy_base_url or not s.innergy_api_key:
            try:
                QMessageBox.warning(
                    self.projects_tab if hasattr(self, 'projects_tab') else None,
                    "Missing Innergy Settings",
                    "The Innergy Base URL or API Key is missing. Please set INNERGY_BASE_URL and INNERGY_API_KEY in your settings (.env) and try again.",
                )
            except Exception:  # pragma: no cover
                # Headless fallback
                print("Missing Innergy settings: set INNERGY_BASE_URL and INNERGY_API_KEY")  # pragma: no cover
            logger.warning("Blocked import: missing Innergy settings")
            return
        # Start background job
        self._import_worker, self._import_thread = run_in_thread(self.data_manager.sync_projects_from_innergy)
        # Upon completion, reload projects in the GUI thread
        self._import_worker.finished.connect(self.load_projects)
        # Wire errors to UI popup and logger
        self._import_worker.error.connect(self._on_import_error)
        logger.info("Triggered background Innergy import")

    @Slot(str)
    def _on_import_error(self, message: str):
        logger = get_logger(__name__)
        logger.error("Innergy import failed: %s", message)
        try:
            QMessageBox.critical(
                self.projects_tab,
                "Import Failed",
                f"Import from Innergy failed:\n{message}\n\nCheck settings (API key/Base URL) and try again.",
            )
        except Exception:
            # Headless fallback (e.g., tests without a QWidget environment)
            print(f"Import error: {message}")

    @Slot(object)
    def open_project(self, project):
        """Opens a project and displays its details in the project detail view."""
        detailed_project = self.data_manager.get_project_by_id(project.id)
        self.projects_detail_view.display_project(detailed_project)
        self.project_opened_signal.emit(detailed_project)

    @Slot(dict)
    def save_project(self, project_data):
        """Saves project data and refreshes the project list."""
        self.data_manager.save_project(project_data)
        self.load_projects()