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

    During MVVM migration, delegates data-loading logic to ProjectsViewModel
    when available, keeping UI-specific concerns (dialogs/threads) here.
    """
    project_opened_signal = Signal(object)

    def __init__(self, data_manager, projects_tab, projects_detail_view, view_model=None):
        super().__init__()
        self.data_manager = data_manager
        self.projects_tab = projects_tab
        self.projects_detail_view = projects_detail_view
        self.view_model = view_model
        self._import_thread = None
        self._import_worker = None
        self._progress_dialog = None
        self._imported_count = 0
        self._import_had_error = False
        # Pending products staged from Innergy (legacy flow)
        self._pending_products = None

        # If a ViewModel is provided, subscribe to its events to update the View
        try:
            if self.view_model is not None and hasattr(self.view_model, "project_opened"):
                self.view_model.project_opened.subscribe(self._on_vm_project_opened)
        except Exception:
            pass

        self._connect_signals()
        self.load_projects()

    def _connect_signals(self):
        self.projects_tab.open_project_signal.connect(self.open_project)
        self.projects_detail_view.save_button_clicked_signal.connect(self.save_project)
        # Wire import to async handler
        if hasattr(self.projects_tab, 'import_projects_signal'):
            self.projects_tab.import_projects_signal.connect(self.import_from_innergy)
        # Wire product load/save actions from detail view (legacy controller path)
        try:
            if hasattr(self.projects_detail_view, 'load_products_clicked_signal'):
                self.projects_detail_view.load_products_clicked_signal.connect(self._on_load_products_from_innergy)
            if hasattr(self.projects_detail_view, 'save_products_changes_clicked_signal'):
                self.projects_detail_view.save_products_changes_clicked_signal.connect(self._on_save_products_changes)
        except Exception:
            pass

    @Slot()
    def load_projects(self):
        """Loads all projects and displays them in the projects tab.

        Delegates to ProjectsViewModel when available.
        """
        try:
            if self.view_model is not None and hasattr(self.view_model, "load_projects"):
                projects = self.view_model.load_projects()
            else:
                projects = self.data_manager.get_all_projects()
            self.projects_tab.display_projects(projects)
        except Exception:
            # Be resilient in UI contexts
            try:
                self.projects_tab.display_projects([])
            except Exception:
                pass

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

    # ---- Products (legacy controller path for ProjectsDetailView button) ----
    def _normalize_products_for_compare(self, products_list):
        """Return a sorted, normalized structure for stable product equality compare.
        Includes extended attributes if present to avoid false mismatches.
        """
        norm = []
        for d in (products_list or []):
            if isinstance(d, dict):
                name = d.get("name") or ""
                qty = d.get("quantity")
                desc = d.get("description") or ""
                cfs = d.get("custom_fields") or []
                loc = d.get("location") or ""
                width = d.get("width")
                height = d.get("height")
                depth = d.get("depth")
                xo = d.get("x_origin")
                yo = d.get("y_origin")
                zo = d.get("z_origin")
                item_no = d.get("item_number") or ""
                comment = d.get("comment") or ""
                angle = d.get("angle")
                link_sg = d.get("link_id_specification_group")
                link_loc = d.get("link_id_location")
                link_wall = d.get("link_id_wall")
                file_name = d.get("file_name") or ""
                picture_name = d.get("picture_name") or ""
            else:
                name = getattr(d, "name", "")
                qty = getattr(d, "quantity", None)
                desc = getattr(d, "description", "")
                cfs = getattr(d, "custom_fields", []) or []
                loc = getattr(d, "location", "") if hasattr(d, "location") else ""
                width = getattr(d, "width", None)
                height = getattr(d, "height", None)
                depth = getattr(d, "depth", None)
                xo = getattr(d, "x_origin", None)
                yo = getattr(d, "y_origin", None)
                zo = getattr(d, "z_origin", None)
                item_no = getattr(d, "item_number", "")
                comment = getattr(d, "comment", "")
                angle = getattr(d, "angle", None)
                link_sg = getattr(d, "link_id_specification_group", None)
                link_loc = getattr(d, "link_id_location", None)
                link_wall = getattr(d, "link_id_wall", None)
                file_name = getattr(d, "file_name", "")
                picture_name = getattr(d, "picture_name", "")
            cf_pairs = []
            for cf in cfs:
                if isinstance(cf, dict):
                    cf_pairs.append((cf.get("name") or "", cf.get("value")))
                else:
                    cf_pairs.append((getattr(cf, "name", ""), getattr(cf, "value", None)))
            cf_pairs.sort()
            norm.append((name, qty, desc, loc, width, height, depth, xo, yo, zo, item_no, comment, angle, link_sg, link_loc, link_wall, file_name, picture_name, tuple(cf_pairs)))
        norm.sort()
        return norm

    @Slot()
    def _on_load_products_from_innergy(self):
        # Determine current project context from the tab
        project = getattr(self.projects_tab, "current_project", None)
        if project is None or self.data_manager is None:
            return
        num = getattr(project, "number", None)
        pid = getattr(project, "id", None)
        if not num or pid is None:
            return
        # Show a simple progress dialog only if API key configured
        try:
            s = get_settings()
        except Exception:
            s = None
        has_api_key = bool(getattr(s, "innergy_api_key", None))
        dlg = None
        try:
            if has_api_key:
                dlg = QProgressDialog("Loading products from Innergy...", "", 0, 0, self.projects_detail_view)
                try:
                    dlg.setCancelButton(None)
                except Exception:
                    pass
                dlg.setWindowModality(dlg.windowModality())
                dlg.setAutoClose(True)
                dlg.setMinimumDuration(0)
                dlg.show()
            # Fetch products from API
            fetched = self.data_manager.fetch_products_from_innergy(str(num)) or []
        finally:
            try:
                if dlg is not None:
                    dlg.close()
            except Exception:
                pass
        # Compare with DB
        try:
            current_db = self.data_manager.get_products_for_project_from_project_db(pid) or []
        except Exception:
            current_db = []
        if self._normalize_products_for_compare(fetched) == self._normalize_products_for_compare(current_db):
            try:
                QMessageBox.information(self.projects_detail_view, "No Changes", "No changes were discovered.")
            except Exception:
                pass
            try:
                self.projects_detail_view.set_save_products_changes_enabled(False)
            except Exception:
                pass
            self._pending_products = None
            return
        # Stage and update UI (without persisting)
        self._pending_products = list(fetched)
        try:
            self.projects_detail_view.update_products_from_dicts(fetched)
        except Exception:
            pass
        try:
            self.projects_detail_view.set_save_products_changes_enabled(True)
        except Exception:
            pass

    @Slot()
    def _on_save_products_changes(self):
        project = getattr(self.projects_tab, "current_project", None)
        if project is None or self.data_manager is None:
            return
        pid = getattr(project, "id", None)
        if pid is None:
            return
        if not self._pending_products:
            return
        ok = False
        try:
            ok = self.data_manager.replace_products_for_project(pid, self._pending_products)
        except Exception:
            ok = False
        if ok:
            # Clear pending and disable Save Changes
            self._pending_products = None
            try:
                self.projects_detail_view.set_save_products_changes_enabled(False)
            except Exception:
                pass
            # Reload enriched project for display
            try:
                enriched = self.data_manager.get_full_project_from_project_db(pid)
                if enriched is not None:
                    # Re-render in both detail view and tab (if supported)
                    self.projects_detail_view.display_project(enriched)
                    if hasattr(self.projects_tab, 'display_project_details'):
                        self.projects_tab.display_project_details(enriched)
            except Exception:
                pass
        else:
            try:
                QMessageBox.critical(self.projects_detail_view, "Save Failed", "Failed to save products changes to the project database.")
            except Exception:
                pass

    @Slot(object)
    def open_project(self, project):
        """Opens a project and displays its details in the project detail view.

        Delegates to ProjectsViewModel when available; otherwise uses DataManager.
        """
        try:
            if self.view_model is not None and hasattr(self.view_model, "open_project"):
                # Let the VM fetch and emit; our subscribed handler will update the view
                self.view_model.open_project(project)
                return
            # Fallback legacy path
            detailed_project = self.data_manager.get_project_by_id(project.id)
            self._render_project(detailed_project)
        except Exception:
            # Best-effort resilience in UI context
            pass

    # --- VM event handlers ---
    def _on_vm_project_opened(self, detailed_project):
        try:
            self._render_project(detailed_project)
        except Exception:
            pass

    # --- Helpers ---
    def _render_project(self, detailed_project):
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