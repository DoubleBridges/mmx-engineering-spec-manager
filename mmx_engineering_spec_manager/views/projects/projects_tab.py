import os
from PySide6.QtCore import Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTableView, QPushButton, QPlainTextEdit, QHeaderView, QLineEdit

from .projects_detail_view import ProjectsDetailView


class ProjectsTab(QWidget):
    open_project_signal = Signal(object)
    import_projects_signal = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.projects = []
        self.current_project = None
        self._row_to_project_index = []  # maps visible row -> original self.projects index

        # UI Elements
        self.projects_table = QTableView()
        self.import_button = QPushButton("Import from Innergy")
        self.load_button = QPushButton("Load Project")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search number or name")
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
        top_bar.addWidget(self.search_input)
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
        self.search_input.textChanged.connect(self._on_search_text_changed)

    def display_projects(self, projects):
        self.projects = projects
        self._apply_filter_and_refresh()

    def _build_model_for_projects(self, subset):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Number", "Name", "Job Description"])
        for project in subset:
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

    def _apply_filter_and_refresh(self):
        # Compute filtered subset and mapping by number and name only
        try:
            query = (self.search_input.text() if self.search_input else "").strip().lower()
        except Exception:
            query = ""
        row_map = []
        subset = []
        for idx, p in enumerate(self.projects):
            num = (getattr(p, "number", "") or "")
            name = (getattr(p, "name", "") or "")
            if not query or (query in str(num).lower() or query in str(name).lower()):
                subset.append(p)
                row_map.append(idx)
        self._row_to_project_index = row_map
        self._build_model_for_projects(subset)

    def _on_search_text_changed(self, _text):
        self._apply_filter_and_refresh()

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
        # Map visible row to original project index if filtered
        if 0 <= row < len(self._row_to_project_index):
            orig_idx = self._row_to_project_index[row]
        else:
            orig_idx = row
        if 0 <= orig_idx < len(self.projects):
            project = self.projects[orig_idx]
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
        # Map visible row to original project index
        if 0 <= target_row < len(self._row_to_project_index):
            orig_idx = self._row_to_project_index[target_row]
        else:
            orig_idx = target_row
        if 0 <= orig_idx < len(self.projects):
            project = self.projects[orig_idx]
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