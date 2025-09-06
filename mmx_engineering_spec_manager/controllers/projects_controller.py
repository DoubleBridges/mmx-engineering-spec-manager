import os
import json
from PySide6.QtCore import QObject, Slot, Signal
from PySide6.QtWidgets import QMessageBox, QProgressDialog

from mmx_engineering_spec_manager.utilities.async_worker import run_in_thread
from mmx_engineering_spec_manager.utilities.logging_config import get_logger
from mmx_engineering_spec_manager.utilities.settings import get_settings
from mmx_engineering_spec_manager.importers.innergy import InnergyImporter


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
        self._progress_dialog = None
        self._imported_count = 0
        self._import_had_error = False

        self._connect_signals()
        self.load_projects()

    def _connect_signals(self):
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
        """Run Innergy sync in background and refresh project list when done, or show raw response in debug mode."""
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

        debug_log = os.getenv("DEBUG_SHOW_INNERGY_RESPONSE") == "1"
        can_display_log = hasattr(self.projects_tab, 'display_log_text')
        if debug_log and can_display_log:
            # In debug mode, fetch the raw response and show it in the projects tab log view
            importer = InnergyImporter()
            def fetch_raw():
                return importer.get_projects_raw()
            worker, thread = run_in_thread(fetch_raw)
            self._import_worker, self._import_thread = worker, thread

            def _on_raw_result(res):
                try:
                    txt = res.get("text", "") if isinstance(res, dict) else str(res)
                    # Try pretty JSON
                    try:
                        parsed = json.loads(txt)
                        pretty = json.dumps(parsed, indent=2)
                        txt_out = f"Status: {res.get('status_code')}\n\n{pretty}" if isinstance(res, dict) else pretty
                    except Exception:  # pragma: no cover
                        txt_out = f"Status: {res.get('status_code')}\n\n{txt}" if isinstance(res, dict) else txt  # pragma: no cover
                    if hasattr(self.projects_tab, 'display_log_text'):
                        self.projects_tab.display_log_text(txt_out)
                except Exception as e:  # pragma: no cover
                    logger.error("Failed to display raw Innergy response: %s", e)
            worker.result.connect(_on_raw_result)
            logger.info("Triggered Innergy raw response fetch for debug log view")
            return

        # Normal path with progress dialog and DB sync
        self._import_had_error = False
        self._imported_count = 0
        try:
            self._progress_dialog = QProgressDialog("Importing projects from Innergy...", "Cancel", 0, 100, self.projects_tab)
            self._progress_dialog.setWindowTitle("Import in progress")
            self._progress_dialog.setAutoClose(False)
            self._progress_dialog.setAutoReset(False)
            self._progress_dialog.setValue(0)
            self._progress_dialog.setMinimumDuration(0)
            self._progress_dialog.show()
        except Exception:  # pragma: no cover
            self._progress_dialog = None

        # Start background job (FunctionWorker injects a progress kwarg automatically)
        self._import_worker, self._import_thread = run_in_thread(self.data_manager.sync_projects_from_innergy)
        # Progress updates
        if self._progress_dialog is not None:
            try:
                self._import_worker.progress.connect(lambda v: self._progress_dialog.setValue(int(v)))
            except Exception:  # pragma: no cover
                pass
        # Capture result (imported count)
        self._import_worker.result.connect(self._on_import_result)
        # Upon completion, reload projects in the GUI thread and finalize UI
        self._import_worker.finished.connect(self.load_projects)
        self._import_worker.finished.connect(self._finalize_import_ui)
        # Wire errors to UI popup and logger
        self._import_worker.error.connect(self._on_import_error)
        logger.info("Triggered background Innergy import")

    @Slot(object)
    def _on_import_result(self, result):
        # Store the imported count if available
        try:
            self._imported_count = int(result) if result is not None else 0
        except Exception:
            self._imported_count = 0

    @Slot()
    def _finalize_import_ui(self):
        # Close/hide the progress dialog if present
        try:
            if self._progress_dialog is not None:
                self._progress_dialog.setValue(100)
                self._progress_dialog.close()
        except Exception:  # pragma: no cover
            pass
        finally:
            self._progress_dialog = None

        # Show success only if no error occurred
        if not self._import_had_error:
            try:
                if int(self._imported_count) == 0:
                    QMessageBox.warning(
                        self.projects_tab if hasattr(self, 'projects_tab') else None,
                        "No Projects Imported",
                        "The Innergy API returned no importable projects.\n\n"
                        "Tips:\n"
                        "- Verify INNERGY_BASE_URL and INNERGY_API_KEY in your settings (.env).\n"
                        "- Ensure your account has access to projects and the API is reachable.",
                    )
                else:
                    QMessageBox.information(
                        self.projects_tab if hasattr(self, 'projects_tab') else None,
                        "Import Complete",
                        f"Successfully imported/updated {self._imported_count} project(s) from Innergy.",
                    )
            except Exception:  # pragma: no cover
                # Headless fallback
                if int(self._imported_count) == 0:
                    print("No projects imported from Innergy")  # pragma: no cover
                else:
                    print(f"Import complete: {self._imported_count} project(s)")  # pragma: no cover

    @Slot(str)
    def _on_import_error(self, message: str):
        logger = get_logger(__name__)
        logger.error("Innergy import failed: %s", message)
        self._import_had_error = True
        # Ensure progress dialog is closed
        try:
            if self._progress_dialog is not None:
                self._progress_dialog.close()  # pragma: no cover
        except Exception:  # pragma: no cover
            pass
        finally:
            self._progress_dialog = None
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
        # Keep existing detail view rendering (covered by tests)
        self.projects_detail_view.display_project(detailed_project)
        # Ask the tab to swap to the detail view if supported
        try:
            if hasattr(self.projects_tab, 'display_project_details'):
                self.projects_tab.display_project_details(detailed_project)
        except Exception:  # pragma: no cover
            # Be resilient in tests/mocks
            pass  # pragma: no cover
        self.project_opened_signal.emit(detailed_project)

    @Slot(dict)
    def save_project(self, project_data):
        """Saves project data and refreshes the project list."""
        self.data_manager.save_project(project_data)
        self.load_projects()