from __future__ import annotations
from typing import List, Dict, Any

from PySide6.QtCore import Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QPushButton,
    QTabWidget,
    QInputDialog,
    QFileDialog,
    QComboBox,
    QStyledItemDelegate,
    QHeaderView,
)

from mmx_engineering_spec_manager.utilities import kv_import
from mmx_engineering_spec_manager.utilities import callout_import
from mmx_engineering_spec_manager.data_manager.manager import DataManager


class AttributesTab(QWidget):
    """
    Attributes tab that can:
    - Load arbitrary CSV/JSON into a simple table via load_from_path (kept for tests/back-compat).
    - Load callouts (CSV/JSON) via the Load File button with dialogs, categorize them, edit in tables, and save to DB.
    """

    load_file_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows: List[Dict[str, Any]] = []
        self._dm = None  # Lazy init to avoid heavy DB setup during tests until needed
        self._callout_tables: Dict[str, QTableView] = {}

        # Existing generic table and Load button (kept for tests)
        self.table = QTableView()
        self.load_button = QPushButton("Load File")
        # Emit existing signal for backward compatibility and call our handler
        self.load_button.clicked.connect(self.load_file_clicked.emit)
        self.load_button.clicked.connect(self._on_load_file_clicked)

        # Save button for callouts
        self.save_button = QPushButton("Save Callouts")
        self.save_button.clicked.connect(self._on_save_callouts)

        # Callouts tab widget with per-category tables
        self.callouts_tabs = QTabWidget()
        self._init_callouts_ui()

        # Layout
        top_bar = QHBoxLayout()
        top_bar.addWidget(self.load_button)
        top_bar.addWidget(self.save_button)
        top_bar.addStretch(1)

        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addWidget(self.callouts_tabs)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def _build_model(self, rows: List[Dict[str, Any]]):
        # Determine union of keys for columns
        keys: List[str] = []
        seen = set()
        for r in rows:
            for k in r.keys():
                if k not in seen:
                    seen.add(k)
                    keys.append(k)
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(keys)
        for r in rows:
            items = [QStandardItem(str(r.get(k, ""))) for k in keys]
            model.appendRow(items)
        self.table.setModel(model)
        # Autosize columns to contents for readability
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)
        self.table.resizeColumnsToContents()

    def _init_callouts_ui(self):
        # Create per-category tables
        headers = ["Type", "Name", "Tag", "Description"]
        for tab_name in ("Finishes", "Hardware", "Sinks", "Appliances", "Uncategorized"):
            view = QTableView()
            model = QStandardItemModel()
            model.setHorizontalHeaderLabels(headers)
            view.setModel(model)
            # Autosize columns to their contents for better readability
            header = view.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
            header.setStretchLastSection(True)
            self.callouts_tabs.addTab(view, tab_name)
            self._callout_tables[tab_name] = view
        # Add combo delegate for Type column in Uncategorized
        class TypeComboDelegate(QStyledItemDelegate):
            def createEditor(self, parent, option, index):
                if index.column() == 0:
                    combo = QComboBox(parent)
                    combo.addItems([callout_import.TYPE_FINISH, callout_import.TYPE_HARDWARE, callout_import.TYPE_SINK, callout_import.TYPE_APPLIANCE, callout_import.TYPE_UNCATEGORIZED])
                    return combo
                return super().createEditor(parent, option, index)
            def setEditorData(self, editor, index):
                if isinstance(editor, QComboBox):
                    val = index.data() or ""
                    i = editor.findText(str(val))
                    editor.setCurrentIndex(max(0, i))
                else:
                    super().setEditorData(editor, index)
            def setModelData(self, editor, model, index):
                if isinstance(editor, QComboBox):
                    model.setData(index, editor.currentText())
                else:
                    super().setModelData(editor, model, index)
        self._uncat_delegate = TypeComboDelegate(self)
        self._callout_tables["Uncategorized"].setItemDelegateForColumn(0, self._uncat_delegate)

    def _populate_callout_table(self, tab_name: str, rows: List[Dict[str, Any]]):
        view = self._callout_tables.get(tab_name)
        if not view:
            return
        model: QStandardItemModel = view.model()  # type: ignore[assignment]
        model.removeRows(0, model.rowCount())
        for r in rows:
            items = [QStandardItem(str(r.get(k, ""))) for k in ("Type", "Name", "Tag", "Description")]
            for it in items:
                it.setEditable(True)
            model.appendRow(items)
        # Adjust columns after data changes
        try:
            view.resizeColumnsToContents()
        except Exception:
            pass

    def _rows_from_model(self, view: QTableView) -> List[Dict[str, Any]]:
        model: QStandardItemModel = view.model()  # type: ignore[assignment]
        rows: List[Dict[str, Any]] = []
        for i in range(model.rowCount()):
            row = {
                "Type": model.item(i, 0).text() if model.item(i, 0) else "",
                "Name": model.item(i, 1).text() if model.item(i, 1) else "",
                "Tag": model.item(i, 2).text() if model.item(i, 2) else "",
                "Description": model.item(i, 3).text() if model.item(i, 3) else "",
            }
            # Skip fully empty rows
            if any(row.values()):
                rows.append(row)
        return rows

    def _on_load_file_clicked(self):
        # Choose file type
        file_type, ok = QInputDialog.getItem(self, "Select File Type", "Type:", ["CSV", "JSON"], 0, False)
        if not ok:
            return
        # Select file
        if file_type == "CSV":
            filt = "CSV Files (*.csv)"
        else:
            filt = "JSON Files (*.json)"
        path, _ = QFileDialog.getOpenFileName(self, f"Open {file_type}", "", filt)
        if not path:
            return
        # Try parsing as callouts first
        dtos = callout_import.read_callouts(file_type, path)
        if dtos:
            grouped = callout_import.group_callouts(dtos)
            # Populate callout tables
            for tab_name, items in grouped.items():
                rows = [
                    {"Type": d.type, "Name": d.name, "Tag": d.tag, "Description": d.description}
                    for d in items
                ]
                self._populate_callout_table(tab_name, rows)
            return
        # Fallback: load generically into the attributes table
        rows = kv_import.read_any(path)
        if not isinstance(rows, list):
            rows = []
        self._rows = rows
        self._build_model(rows)

    def _on_save_callouts(self):
        # Lazy create DataManager only when saving
        if self._dm is None:
            self._dm = DataManager()
        # Collect rows from all tables
        all_rows: List[Dict[str, str]] = []
        for tab_name, view in self._callout_tables.items():
            all_rows.extend(self._rows_from_model(view))
        # Map to DTOs
        dtos = []
        for r in all_rows:
            t = (r.get("Type") or "").strip() or callout_import.TYPE_UNCATEGORIZED
            name = (r.get("Name") or "").strip()
            tag = (r.get("Tag") or "").strip()
            desc = (r.get("Description") or "").strip()
            if not name or not tag or not desc:
                continue
            dtos.append(callout_import._mk_dto(name, tag, desc))
            # Preserve explicit user-assigned Type in Uncategorized by overriding categorization
            if t and t != dtos[-1].type:
                dtos[-1].type = t  # type: ignore[misc]
        # Choose project to save into
        projects = self._dm.get_all_projects()
        if not projects:
            return
        items = [f"{p.number or ''} - {p.name or ''} (ID {p.id})" for p in projects]
        choice, ok = QInputDialog.getItem(self, "Select Project", "Project:", items, 0, False)
        if not ok:
            return
        sel_idx = items.index(choice)
        project = projects[sel_idx]
        # Group and persist
        grouped = callout_import.group_callouts(dtos)
        self._dm.replace_callouts_for_project(project.id, grouped)

    def load_from_path(self, path: str):
        rows = kv_import.read_any(path)
        if not isinstance(rows, list):
            rows = []
        self._rows = rows
        self._build_model(rows)

    def current_rows(self) -> List[Dict[str, Any]]:
        return list(self._rows)
