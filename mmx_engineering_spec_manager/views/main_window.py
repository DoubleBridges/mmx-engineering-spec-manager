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

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Engineering Project Manager")
        self.resize(1200, 800)

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