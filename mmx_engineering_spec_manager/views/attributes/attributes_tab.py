from __future__ import annotations
from typing import List, Dict, Any

from PySide6.QtCore import Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QPushButton

from mmx_engineering_spec_manager.utilities import kv_import


class AttributesTab(QWidget):
    """
    Minimal tab to load JSON/CSV key-value/project properties and display them in a table.
    For MVP, only programmatic load is provided; UI "Load File" button emits a signal for future wiring.
    """

    load_file_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._rows: List[Dict[str, Any]] = []

        self.table = QTableView()
        self.load_button = QPushButton("Load File")
        self.load_button.clicked.connect(self.load_file_clicked.emit)

        layout = QVBoxLayout()
        layout.addWidget(self.load_button)
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

    def load_from_path(self, path: str):
        rows = kv_import.read_any(path)
        if not isinstance(rows, list):
            rows = []
        self._rows = rows
        self._build_model(rows)

    def current_rows(self) -> List[Dict[str, Any]]:
        return list(self._rows)
