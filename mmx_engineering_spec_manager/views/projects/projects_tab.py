import os
from PySide6.QtCore import Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QPushButton, QPlainTextEdit

from .projects_detail_view import ProjectsDetailView


class ProjectsTab(QWidget):
    open_project_signal = Signal(object)
    import_projects_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.projects = []
        self.current_project = None

        # UI Elements
        self.projects_table = QTableView()
        self.import_button = QPushButton("Import from Innergy")
        self.projects_detail_view = ProjectsDetailView()
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.import_button)

        # Temporarily switch table to log view when debug flag is set
        if os.getenv("DEBUG_SHOW_INNERGY_RESPONSE") == "1":
            layout.addWidget(self.log_view)
        else:
            layout.addWidget(self.projects_table)

        self.setLayout(layout)

        self._connect_signals()

    def _connect_signals(self):
        self.import_button.clicked.connect(self.import_projects_signal.emit)
        self.projects_table.doubleClicked.connect(self.on_project_double_clicked)

    def display_projects(self, projects):
        self.projects = projects
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Number", "Name", "Job Description"])
        for project in projects:
            row = [
                QStandardItem(getattr(project, "number", "")),
                QStandardItem(getattr(project, "name", "")),
                QStandardItem(getattr(project, "job_description", "")),
            ]
            model.appendRow(row)
        self.projects_table.setModel(model)
        # Enlarge 2nd and 3rd columns (index 1 and 2) to be 3x wider than baseline
        try:
            header = self.projects_table.horizontalHeader()
            for col in (1, 2):
                base = max(self.projects_table.columnWidth(col), header.sectionSizeHint(col))
                new_w = int(base * 3)
                header.resizeSection(col, new_w)
        except Exception:  # pragma: no cover
            # If running in a headless/special environment where header isn't available, ignore
            pass  # pragma: no cover

    def display_log_text(self, text: str):
        try:
            self.log_view.setPlainText(text)
        except Exception:
            pass

    def on_project_double_clicked(self, index):
        row = index.row()
        if 0 <= row < len(self.projects):
            project = self.projects[row]
            self.open_project_signal.emit(project)

    def display_project_details(self, project):
        self.current_project = project
        # In a real app, you might switch to a details view; for tests we just store it.
        try:
            self.projects_detail_view.display_project(project)
        except Exception:
            # If detail view cannot render due to mock, ignore for test environment
            pass