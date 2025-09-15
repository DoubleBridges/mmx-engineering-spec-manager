import os
from PySide6.QtCore import Signal, QTimer, Qt, QCoreApplication
from PySide6.QtGui import QCloseEvent, QAction
from PySide6.QtWidgets import (QMainWindow, QTabWidget, QProgressDialog, QMessageBox)

from .export.export_tab import ExportTab
from .projects.projects_tab import ProjectsTab
from .workspace.workspace_tab import WorkspaceTab
from .attributes.attributes_tab import AttributesTab
from mmx_engineering_spec_manager.utilities.settings import get_settings
from mmx_engineering_spec_manager.utilities.persistence import project_sqlite_db_path


class MainWindow(QMainWindow):
    window_ready_signal = Signal()
    close_event_signal = Signal()
    refresh_requested = Signal()
    current_project_changed = Signal(object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Engineering Project Manager")
        self.resize(1200, 800)
        self.current_project = None
        self._vm = None  # MainWindowViewModel (optional)

        # Create the menu bar
        self.menu_bar = self.menuBar()

        # Add the 'File' menu
        self.file_menu = self.menu_bar.addMenu("&File")
        self.file_menu.setObjectName("file_menu")

        # Add the 'Exit' action to the 'File' menu
        self.exit_action = QAction("E&xit", self)
        self.file_menu.addAction(self.exit_action)

        # Connect the 'Exit' action to the close method
        self.exit_action.triggered.connect(self.close)

        # Add the 'View' menu with Refresh action (F5)
        self.view_menu = self.menu_bar.addMenu("&View")
        self.view_menu.setObjectName("view_menu")
        self.refresh_action = QAction("&Refresh", self)
        self.refresh_action.setShortcut("F5")
        self.view_menu.addAction(self.refresh_action)
        # Keep existing Qt signal for backward compatibility
        self.refresh_action.triggered.connect(self.refresh_requested.emit)

        # Create the QTabWidget and set it as the central widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Create and add the 'Projects' tab
        self.projects_tab = ProjectsTab()
        self.projects_detail_view = self.projects_tab.projects_detail_view
        self.tab_widget.addTab(self.projects_tab, "Projects")
        # Wire detail view actions
        try:
            self.projects_detail_view.load_products_clicked_signal.connect(self._on_load_products_from_innergy)
            self.projects_detail_view.save_products_changes_clicked_signal.connect(self._on_save_products_changes)
        except Exception:
            pass
        self._pending_products = None
        
        # No DataManager in View (MVVM). Keep attribute for legacy no-op handlers.
        self._data_manager = None

        # Try to build and attach a ViewModel (transitional wiring)
        try:
            from mmx_engineering_spec_manager.core.composition_root import build_main_window_view_model
            self._vm = build_main_window_view_model()
            # Relay VM refresh requests to existing Qt signal so controllers keep working
            self._vm.refresh_requested.subscribe(lambda: self.refresh_requested.emit())
            # Forward UI Refresh action to VM
            self.refresh_action.triggered.connect(self._vm.request_refresh)
            # Route project open via VM; VM then notifies back to lightweight handler
            self.projects_tab.open_project_signal.connect(self._vm.set_active_project)
            self._vm.project_opened.subscribe(self._on_project_opened_from_vm)
        except Exception:
            self._vm = None  # pragma: no cover
            # Fallback: connect project open directly to existing handler
            self.projects_tab.open_project_signal.connect(self._on_project_loaded)

        # Insert new Attributes tab between Projects and Workspace
        self.attributes_tab = AttributesTab()
        self.tab_widget.addTab(self.attributes_tab, "Attributes")
        # Transitional: build an AttributesViewModel and attach non-invasively
        try:
            from mmx_engineering_spec_manager.core.composition_root import build_attributes_view_model
            self._attributes_vm = build_attributes_view_model()
            try:
                self.attributes_tab.set_view_model(self._attributes_vm)
            except Exception:
                pass
            if self._vm is not None:
                # Bridge MainWindow VM project selection to Attributes VM
                self._vm.project_opened.subscribe(self._attributes_vm.set_active_project)
        except Exception:
            self._attributes_vm = None  # pragma: no cover

        self.workspace_tab = WorkspaceTab()
        self.tab_widget.addTab(self.workspace_tab, "Workspace")
        # Transitional: build a WorkspaceViewModel and attach non-invasively
        try:
            from mmx_engineering_spec_manager.core.composition_root import build_workspace_view_model
            self._workspace_vm = build_workspace_view_model()
            try:
                self.workspace_tab.set_view_model(self._workspace_vm)
            except Exception:
                pass
            # Bridge MainWindow VM project selection to Workspace VM and View
            if self._vm is not None:
                self._vm.project_opened.subscribe(self._workspace_vm.set_active_project)
                self._vm.project_opened.subscribe(self.workspace_tab.display_project_data)
        except Exception:
            self._workspace_vm = None  # pragma: no cover

        self.export_tab = ExportTab()
        self.tab_widget.addTab(self.export_tab, "Export")

        # Cache tab indexes
        self._idx_projects = self.tab_widget.indexOf(self.projects_tab)
        self._idx_attributes = self.tab_widget.indexOf(self.attributes_tab)
        self._idx_workspace = self.tab_widget.indexOf(self.workspace_tab)
        self._idx_export = self.tab_widget.indexOf(self.export_tab)

        # Disable non-project tabs until a current project is set
        self._set_non_project_tabs_enabled(False)

        # React when user switches tabs (for lazy loading of Attributes content)
        try:
            self.tab_widget.currentChanged.connect(self._on_tab_changed)
        except Exception:  # pragma: no cover
            pass  # pragma: no cover
        # Focus Projects search field when window becomes ready
        try:
            self.window_ready_signal.connect(self._focus_projects_search)
        except Exception:  # pragma: no cover
            pass  # pragma: no cover

    def _set_non_project_tabs_enabled(self, enabled: bool):
        try:
            self.tab_widget.setTabEnabled(self._idx_attributes, enabled)
            self.tab_widget.setTabEnabled(self._idx_workspace, enabled)
            self.tab_widget.setTabEnabled(self._idx_export, enabled)
        except Exception:
            pass

    def set_current_project(self, project):
        self.current_project = project
        try:
            self.current_project_changed.emit(project)
        except Exception:
            pass

    def _on_project_opened_from_vm(self, project):
        """Lightweight handler for VM-originated project activation.

        Only updates the UI; no DataManager orchestration or I/O here.
        """
        # Set current project and display details
        self.set_current_project(project)
        try:
            self.projects_tab.display_project_details(project)
        except Exception:
            pass
        # Inform Attributes tab about the active project
        try:
            self.attributes_tab.set_active_project(project)
            if self.tab_widget.currentIndex() == self._idx_attributes:
                self.attributes_tab.load_callouts_for_active_project()
        except Exception:
            pass
        # Update Workspace view presentation (safe, view-only)
        try:
            self.workspace_tab.display_project_data(project)
        except Exception:
            pass
        # Enable other tabs now that a project is active
        self._set_non_project_tabs_enabled(True)

    def _on_project_loaded(self, project):
        # Set current project, show details, and enable other tabs
        self.set_current_project(project)
        try:
            project_to_show = project
            if getattr(self, "_data_manager", None) is not None:
                # Determine per-project DB path BEFORE preparing, so we can detect prior existence
                try:
                    db_path = project_sqlite_db_path(project)
                except Exception:
                    db_path = None
                existed_already = bool(db_path and os.path.exists(db_path))
                # Ensure the project's dedicated SQLite DB and schema exists
                try:
                    self._data_manager.prepare_project_db(project)
                except Exception:  # pragma: no cover
                    pass  # pragma: no cover
                num = getattr(project, "number", None)
                pid = getattr(project, "id", None)
                # If a DB file existed already, prefer loading from it and SKIP any API calls
                if existed_already and pid is not None:
                    try:
                        enriched = self._data_manager.get_full_project_from_project_db(pid)
                        if enriched is not None:
                            project_to_show = enriched
                            # Show details without attempting ingestion
                            self.projects_tab.display_project_details(project_to_show)
                            # Inform Attributes about active project
                            try:
                                self.attributes_tab.set_active_project(project)
                                if self.tab_widget.currentIndex() == self._idx_attributes:
                                    self.attributes_tab.load_callouts_for_active_project()
                            except Exception:
                                pass
                            self._set_non_project_tabs_enabled(True)
                            return
                    except Exception:
                        # If load fails, fall back to the ingestion path below
                        pass
                # Otherwise, fall back to ingestion path (only if number is present)
                if num:
                    success = None
                    error_text = None
                    try:
                        settings = get_settings()
                    except Exception:
                        settings = None
                    has_api_key = bool(getattr(settings, "innergy_api_key", None))
                    dlg = None
                    try:
                        if has_api_key:
                            dlg = QProgressDialog("Loading project details from Innergy...", "", 0, 0, self)
                            try:
                                dlg.setCancelButton(None)
                            except Exception:
                                pass
                            dlg.setWindowModality(Qt.WindowModal)
                            dlg.setAutoClose(True)
                            dlg.setMinimumDuration(0)
                            dlg.show()
                            try:
                                QCoreApplication.processEvents()
                            except Exception:
                                pass
                        # Perform ingestion (blocking)
                        try:
                            success = self._data_manager.ingest_project_details_to_project_db(str(num))
                        except Exception as e:
                            error_text = str(e)
                            success = False
                    finally:
                        try:
                            if dlg is not None:
                                dlg.close()
                        except Exception:
                            pass
                    # If API key was present and ingestion failed, surface an error
                    if has_api_key and not success:
                        try:
                            msg = f"Failed to load project details from Innergy for project {num}."
                            if error_text:
                                msg += f"\nDetails: {error_text}"
                            QMessageBox.critical(self, "Innergy Load Failed", msg)
                        except Exception:
                            pass
                    # Try to load enriched project from per-project DB regardless
                    try:
                        enriched = self._data_manager.get_full_project_from_project_db(pid)
                        if enriched is not None:
                            project_to_show = enriched
                    except Exception:
                        pass
            self.projects_tab.display_project_details(project_to_show)
        except Exception:
            pass
        # Inform Attributes tab about the active project
        try:
            self.attributes_tab.set_active_project(project)
            # If Attributes tab is already selected, load callouts now
            if self.tab_widget.currentIndex() == self._idx_attributes:
                self.attributes_tab.load_callouts_for_active_project()
        except Exception:
            pass
        self._set_non_project_tabs_enabled(True)

    def _focus_projects_search(self):
        """Set initial focus to the Projects tab search field when the window is ready."""
        try:
            # Ensure Projects tab is selected then focus the search input
            self.tab_widget.setCurrentIndex(self._idx_projects)
            self.projects_tab.search_input.setFocus()
        except Exception:
            pass

    def _on_tab_changed(self, index: int):
        try:
            if index == self._idx_attributes and self.current_project is not None:
                # Ensure Attributes tab knows the current project and load callouts
                self.attributes_tab.set_active_project(self.current_project)
                self.attributes_tab.load_callouts_for_active_project()
        except Exception:
            pass

    # --- Innergy Products Load/Save workflow ---
    def _normalize_products_for_compare(self, products_list):
        """Return a sorted list of tuples for stable equality compare including extended attributes."""
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

    def _on_load_products_from_innergy(self):
        project = getattr(self, "current_project", None)
        if project is None or getattr(self, "_data_manager", None) is None:
            return
        num = getattr(project, "number", None)
        pid = getattr(project, "id", None)
        if not num or pid is None:
            return
        # Show progress only if API key configured
        try:
            settings = get_settings()
        except Exception:
            settings = None
        has_api_key = bool(getattr(settings, "innergy_api_key", None))
        dlg = None
        try:
            if has_api_key:
                dlg = QProgressDialog("Loading products from Innergy...", "", 0, 0, self)
                try:
                    dlg.setCancelButton(None)
                except Exception:
                    pass
                dlg.setWindowModality(Qt.WindowModal)
                dlg.setAutoClose(True)
                dlg.setMinimumDuration(0)
                dlg.show()
                try:
                    QCoreApplication.processEvents()
                except Exception:
                    pass
            # Fetch products
            fetched = self._data_manager.fetch_products_from_innergy(str(num)) or []
        finally:
            try:
                if dlg is not None:
                    dlg.close()
            except Exception:
                pass
        # Compare with current DB products
        try:
            current_db = self._data_manager.get_products_for_project_from_project_db(pid) or []
        except Exception:
            current_db = []
        if self._normalize_products_for_compare(fetched) == self._normalize_products_for_compare(current_db):
            try:
                QMessageBox.information(self, "No Changes", "No changes were discovered.")
            except Exception:
                pass
            try:
                self.projects_detail_view.set_save_products_changes_enabled(False)
            except Exception:
                pass
            self._pending_products = None
            return
        # Show fetched products in the detail tree without persisting
        self._pending_products = fetched
        # Update (do not replace) the existing tree's Locations subtree
        try:
            self.projects_detail_view.update_products_from_dicts(fetched)
        except Exception:
            pass
        try:
            self.projects_detail_view.set_save_products_changes_enabled(True)
        except Exception:
            pass

    def _on_save_products_changes(self):
        project = getattr(self, "current_project", None)
        if project is None or getattr(self, "_data_manager", None) is None:
            return
        pid = getattr(project, "id", None)
        if pid is None:
            return
        if not self._pending_products:
            return
        ok = False
        try:
            ok = self._data_manager.replace_products_for_project(pid, self._pending_products)
        except Exception:
            ok = False
        if ok:
            # Clear pending and disable button
            self._pending_products = None
            try:
                self.projects_detail_view.set_save_products_changes_enabled(False)
            except Exception:
                pass
            # Reload enriched project from per-project DB and display
            try:
                enriched = self._data_manager.get_full_project_from_project_db(pid)
                if enriched is not None:
                    self.projects_tab.display_project_details(enriched)
            except Exception:
                pass
        else:
            try:
                QMessageBox.critical(self, "Save Failed", "Failed to save products changes to the project database.")
            except Exception:
                pass

    def show(self):
        super().show()
        QTimer.singleShot(0, self.window_ready_signal.emit)

    def closeEvent(self, event):
        """
        Overrides the close event to emit a custom signal.
        """
        self.close_event_signal.emit()
        event.accept()
        super().closeEvent(event)