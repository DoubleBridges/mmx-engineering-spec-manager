from PySide6.QtCore import Signal
from PySide6.QtGui import QCloseEvent, QAction
from PySide6.QtWidgets import (QMainWindow, QTabWidget)

from .export.export_tab import ExportTab
from .projects.projects_tab import ProjectsTab
from .workspace.workspace_tab import WorkspaceTab
from .attributes.attributes_tab import AttributesTab
from PySide6.QtCore import QTimer


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
        self.refresh_action.triggered.connect(self.refresh_requested.emit)

        # Create the QTabWidget and set it as the central widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Create and add the 'Projects' tab
        self.projects_tab = ProjectsTab()
        self.projects_detail_view = self.projects_tab.projects_detail_view
        self.tab_widget.addTab(self.projects_tab, "Projects")

        # Insert new Attributes tab between Projects and Workspace
        self.attributes_tab = AttributesTab()
        self.tab_widget.addTab(self.attributes_tab, "Attributes")

        self.workspace_tab = WorkspaceTab()
        self.tab_widget.addTab(self.workspace_tab, "Workspace")

        self.export_tab = ExportTab()
        self.tab_widget.addTab(self.export_tab, "Export")

        # Cache tab indexes
        self._idx_projects = self.tab_widget.indexOf(self.projects_tab)
        self._idx_attributes = self.tab_widget.indexOf(self.attributes_tab)
        self._idx_workspace = self.tab_widget.indexOf(self.workspace_tab)
        self._idx_export = self.tab_widget.indexOf(self.export_tab)

        # Disable non-project tabs until a current project is set
        self._set_non_project_tabs_enabled(False)

        # Connect project load events
        self.projects_tab.open_project_signal.connect(self._on_project_loaded)

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

    def _on_project_loaded(self, project):
        # Set current project, show details, and enable other tabs
        self.set_current_project(project)
        try:
            self.projects_tab.display_project_details(project)
        except Exception:
            pass
        self._set_non_project_tabs_enabled(True)

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