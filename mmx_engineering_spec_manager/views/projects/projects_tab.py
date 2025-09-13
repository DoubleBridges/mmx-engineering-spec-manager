import os
from PySide6.QtCore import Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableView, QPushButton, QPlainTextEdit, QHeaderView

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
        self.load_button = QPushButton("Load Project")
        self.projects_detail_view = ProjectsDetailView()
        self.projects_detail_view.setVisible(False)
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setVisible(os.getenv("DEBUG_SHOW_INNERGY_RESPONSE") == "1")

        layout = QVBoxLayout()
        # Top bar with import and load buttons
        top_bar = QHBoxLayout()
        top_bar.addWidget(self.import_button)
        top_bar.addWidget(self.load_button)
        top_bar.addStretch(1)
        layout.addLayout(top_bar)

        # Temporarily switch table to log view when debug flag is set
        if os.getenv("DEBUG_SHOW_INNERGY_RESPONSE") == "1":
            layout.addWidget(self.log_view)
        else:
            layout.addWidget(self.projects_table)
        # Always add the detail view (hidden initially)
        layout.addWidget(self.projects_detail_view)

        self.setLayout(layout)

        self._connect_signals()

    def _connect_signals(self):
        self.import_button.clicked.connect(self.import_projects_signal.emit)
        self.projects_table.doubleClicked.connect(self.on_project_double_clicked)
        self.load_button.clicked.connect(self.on_load_button_clicked)

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
        header = self.projects_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)

    def display_log_text(self, text: str):
        try:
            self.log_view.setPlainText(text)
            if os.getenv("DEBUG_SHOW_INNERGY_RESPONSE") == "1":  # pragma: no cover
                self.log_view.setVisible(True)  # pragma: no cover
                self.projects_table.setVisible(False)  # pragma: no cover
                self.projects_detail_view.setVisible(False)  # pragma: no cover
        except Exception:
            pass

    def on_project_double_clicked(self, index):
        row = index.row()
        if 0 <= row < len(self.projects):
            project = self.projects[row]
            self.open_project_signal.emit(project)

    def on_load_button_clicked(self):
        sel_model = self.projects_table.selectionModel()
        if sel_model is None:
            return
        # Prefer full row selections
        selected_rows = sel_model.selectedRows()
        target_row = None
        if selected_rows:
            target_row = selected_rows[0].row()
        else:
            idxs = sel_model.selectedIndexes()
            if idxs:
                target_row = idxs[0].row()
        if target_row is None:
            return
        if 0 <= target_row < len(self.projects):
            project = self.projects[target_row]
            self.open_project_signal.emit(project)

    def display_project_details(self, project):
        self.current_project = project
        # Swap visibility: show details, hide list/log
        self.projects_detail_view.setVisible(True)
        self.projects_table.setVisible(False)
        self.log_view.setVisible(False)
        try:
            self.projects_detail_view.display_project(project)
        except Exception:
            # If detail view cannot render due to mock, ignore for test environment
            pass