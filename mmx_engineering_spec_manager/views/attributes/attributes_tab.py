from __future__ import annotations
from typing import List, Dict, Any

from PySide6.QtCore import Signal
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QListView,
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
        self._active_project = None  # Currently active project object (set by MainWindow)
        self._vm = None  # Optional AttributesViewModel (transitional wiring)
        # Location tables state
        self._tag_to_desc: Dict[str, str] = {}
        self._location_tables_by_name: Dict[str, List[Dict[str, Any]]] = {}
        self._current_location_name: str | None = None

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

        # Bottom location tables UI (Locations list + Location Table editor)
        self._init_location_tables_ui()

        # Layout
        top_bar = QHBoxLayout()
        top_bar.addWidget(self.load_button)
        top_bar.addWidget(self.save_button)
        top_bar.addStretch(1)

        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addWidget(self.callouts_tabs)
        layout.addLayout(self._location_bar)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def set_view_model(self, view_model):
        """Attach an AttributesViewModel (optional, transitional).

        View remains operable without a VM; this enables MVVM binding without breaking legacy code.
        """
        try:
            self._vm = view_model
        except Exception:
            self._vm = None

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

    def set_active_project(self, project):
        """Set the active project (from MainWindow)."""
        self._active_project = project
        # Forward to ViewModel if present (transitional wiring)
        try:
            if self._vm is not None:
                self._vm.set_active_project(project)
        except Exception:
            pass

    def load_callouts_for_active_project(self):
        """Load callouts for the active project from VM if present; otherwise fallback to DataManager.

        Populates the per-category tables, rebuilds tag index, and refreshes Locations UI.
        """
        # If a ViewModel is attached, prefer it (keeps business logic out of the View)
        try:
            if self._vm is not None:
                grouped = self._vm.load_callouts_for_active_project()
                if isinstance(grouped, dict) and grouped:
                    for tab_name, rows in grouped.items():
                        self._populate_callout_table(str(tab_name), list(rows or []))
                    # Rebuild tag index and load locations/location-tables after callouts are shown
                    self._rebuild_tag_index()
                    self.load_locations_and_location_tables_for_active_project()
                    return
        except Exception:
            # Fall back to legacy path below if VM errors
            pass

        # Legacy fallback path using DataManager
        if self._dm is None:
            try:
                self._dm = DataManager()
            except Exception:  # pragma: no cover
                return  # pragma: no cover
        if not getattr(self, "_active_project", None):
            return
        try:
            pid = getattr(self._active_project, "id", None)
            if pid is None:
                return
            grouped = self._dm.get_callouts_for_project(pid)
            if not isinstance(grouped, dict):
                return
            # Populate each known tab
            for tab_name, items in grouped.items():
                rows = []
                for d in items or []:
                    # Accept dicts from DataManager
                    if isinstance(d, dict):
                        rows.append({
                            "Type": d.get("Type", ""),
                            "Name": d.get("Name", ""),
                            "Tag": d.get("Tag", ""),
                            "Description": d.get("Description", ""),
                        })
                self._populate_callout_table(tab_name, rows)
            # Rebuild tag index and load locations/location-tables after callouts are shown
            self._rebuild_tag_index()
            self.load_locations_and_location_tables_for_active_project()
        except Exception:  # pragma: no cover
            # Silently ignore in UI context
            pass  # pragma: no cover

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
        except Exception:  # pragma: no cover
            pass  # pragma: no cover
        # Update tag index so Location Table can autofill descriptions by tag
        try:
            self._rebuild_tag_index()
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
        # Preferred: ask ViewModel to parse and provide grouped rows
        try:
            if self._vm is not None:
                grouped = self._vm.parse_callouts_from_path(file_type, path)
                if isinstance(grouped, dict) and grouped:
                    # Populate callout tables if present
                    any_populated = False
                    for tab_name, items in grouped.items():
                        if tab_name == "Generic":
                            # Display in generic table area (legacy)
                            rows = items if isinstance(items, list) else []
                            self._rows = rows
                            self._build_model(rows)
                        else:
                            rows = [
                                {"Type": r.get("Type", ""), "Name": r.get("Name", ""),
                                 "Tag": r.get("Tag", ""), "Description": r.get("Description", "")}
                                for r in (items or [])
                            ]
                            self._populate_callout_table(str(tab_name), rows)
                            any_populated = True
                    if any_populated:
                        return
        except Exception:
            # Fall back to legacy path below if VM errors
            pass
        # Legacy: Try parsing as callouts using utilities
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
        # Preselect the active project if available
        default_idx = 0
        try:
            active_id = getattr(getattr(self, "_active_project", None), "id", None)
            if active_id is not None:
                for i, p in enumerate(projects):
                    if getattr(p, "id", None) == active_id:
                        default_idx = i
                        break
        except Exception:  # pragma: no cover
            pass  # pragma: no cover
        choice, ok = QInputDialog.getItem(self, "Select Project", "Project:", items, default_idx, False)
        if not ok:
            return
        sel_idx = items.index(choice)
        project = projects[sel_idx]
        # Group and persist
        grouped = callout_import.group_callouts(dtos)
        self._dm.replace_callouts_for_project(project.id, grouped)
        # Also persist Location Tables for this project
        try:
            lt_data = self._gather_location_tables_data()
            self._dm.replace_location_tables_for_project(project.id, lt_data)
        except Exception:
            # Non-fatal in UI context
            pass

    def load_from_path(self, path: str):
        rows = kv_import.read_any(path)
        if not isinstance(rows, list):
            rows = []
        self._rows = rows
        self._build_model(rows)

    def current_rows(self) -> List[Dict[str, Any]]:
        return list(self._rows)


    def _init_location_tables_ui(self):
        """Initialize the bottom split UI with Locations list (left) and Location Table (right)."""
        self._location_bar = QHBoxLayout()
        # Locations list
        self.locations_list = QListView()
        self._locations_model = QStandardItemModel()
        self.locations_list.setModel(self._locations_model)
        self._location_bar.addWidget(self.locations_list, 1)
        # Right side: Location table editor (Type, Tag, Description) with row controls
        right_box = QVBoxLayout()
        self.location_table_view = QTableView()
        self._location_table_model = QStandardItemModel()
        self._location_table_model.setHorizontalHeaderLabels(["Type", "Tag", "Description"])
        self.location_table_view.setModel(self._location_table_model)
        header = self.location_table_view.horizontalHeader()
        try:
            # Column sizing: Type autosizes to contents, Tag autosizes, Description stretches to fill remaining space
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setStretchLastSection(False)
        except Exception:
            pass
        right_box.addWidget(self.location_table_view, 1)
        # Buttons bar under the table
        buttons_bar = QHBoxLayout()
        self.btn_add_row = QPushButton("Add Row")
        self.btn_delete_row = QPushButton("Delete Row")
        self.btn_move_up = QPushButton("Move Up")
        self.btn_move_down = QPushButton("Move Down")
        buttons_bar.addWidget(self.btn_add_row)
        buttons_bar.addWidget(self.btn_delete_row)
        buttons_bar.addWidget(self.btn_move_up)
        buttons_bar.addWidget(self.btn_move_down)
        buttons_bar.addStretch(1)
        right_box.addLayout(buttons_bar)
        # Add right side box to the split
        self._location_bar.addLayout(right_box, 3)
        # Connect selection and edits
        try:
            self.locations_list.selectionModel().selectionChanged.connect(self._on_location_selected)  # type: ignore[arg-type]
        except Exception:
            pass
        try:
            self._location_table_model.itemChanged.connect(self._on_location_table_item_changed)
        except Exception:
            pass
        # Connect buttons
        try:
            self.btn_add_row.clicked.connect(self._add_location_table_row)
            self.btn_delete_row.clicked.connect(self._delete_location_table_row)
            self.btn_move_up.clicked.connect(self._move_location_table_row_up)
            self.btn_move_down.clicked.connect(self._move_location_table_row_down)
        except Exception:
            pass

    def _rebuild_tag_index(self):
        """Build a mapping from Tag -> Description using all callouts tables above."""
        tag_to_desc: Dict[str, str] = {}
        for view in self._callout_tables.values():
            model: QStandardItemModel = view.model()  # type: ignore[assignment]
            for i in range(model.rowCount()):
                tag = model.item(i, 2).text() if model.item(i, 2) else ""
                desc = model.item(i, 3).text() if model.item(i, 3) else ""
                if tag:
                    tag_to_desc.setdefault(tag, desc)
        self._tag_to_desc = tag_to_desc

    def _on_location_selected(self, selected, deselected):  # pragma: no cover - UI glue
        try:
            # Save current table rows under previous selection
            self._capture_location_table_rows()
            # Get newly selected location name
            idxs = self.locations_list.selectedIndexes()
            if not idxs:
                self._current_location_name = None
                self._populate_location_table_from_rows([])
                return
            idx = idxs[0]
            name = idx.data() or ""
            self._show_location_table_for(str(name))
        except Exception:
            pass

    def _capture_location_table_rows(self):
        """Read rows from the right table and store them under the currently selected location name."""
        name = self._current_location_name
        if not name:
            return
        rows: List[Dict[str, Any]] = []
        for i in range(self._location_table_model.rowCount()):
            t = self._location_table_model.item(i, 0).text() if self._location_table_model.item(i, 0) else ""
            tag = self._location_table_model.item(i, 1).text() if self._location_table_model.item(i, 1) else ""
            desc = self._location_table_model.item(i, 2).text() if self._location_table_model.item(i, 2) else ""
            if t or tag or desc:
                rows.append({"Type": t, "Tag": tag, "Description": desc})
        self._location_tables_by_name[name] = rows

    def _show_location_table_for(self, name: str):
        self._current_location_name = name
        rows = self._location_tables_by_name.get(name, [])
        self._populate_location_table_from_rows(rows)

    def _populate_location_table_from_rows(self, rows: List[Dict[str, Any]]):
        m = self._location_table_model
        m.blockSignals(True)
        try:
            m.removeRows(0, m.rowCount())
            if rows and len(rows) > 0:
                for r in rows:
                    items = [QStandardItem(str(r.get(k, ""))) for k in ("Type", "Tag", "Description")]
                    for it in items:
                        it.setEditable(True)
                    m.appendRow(items)
            else:
                # Default to 5 blank editable rows when there is no data
                for _ in range(5):
                    items = [QStandardItem(""), QStandardItem(""), QStandardItem("")]
                    for it in items:
                        it.setEditable(True)
                    m.appendRow(items)
        finally:
            m.blockSignals(False)
        try:
            self.location_table_view.resizeColumnsToContents()
        except Exception:
            pass

    def _on_location_table_item_changed(self, item: QStandardItem):  # pragma: no cover - UI glue
        try:
            if item.column() == 1:  # Tag column
                tag = item.text()
                if tag and self._tag_to_desc.get(tag):
                    # If Description empty, auto-fill
                    i = item.row()
                    desc_item = self._location_table_model.item(i, 2)
                    if desc_item is None:
                        desc_item = QStandardItem("")
                        self._location_table_model.setItem(i, 2, desc_item)
                    if not desc_item.text():
                        desc_item.setText(self._tag_to_desc[tag])
        except Exception:
            pass

    def _gather_location_tables_data(self) -> Dict[str, List[Dict[str, Any]]]:
        # Capture current edits
        self._capture_location_table_rows()
        # Return a shallow copy to avoid accidental external modifications
        out: Dict[str, List[Dict[str, Any]]] = {}
        for name, rows in (self._location_tables_by_name or {}).items():
            # Filter out empty rows
            filt = []
            for r in rows or []:
                if any([(r.get("Type") or ""), (r.get("Tag") or ""), (r.get("Description") or "")]):
                    filt.append({
                        "Type": (r.get("Type") or ""),
                        "Tag": (r.get("Tag") or ""),
                        "Description": (r.get("Description") or ""),
                    })
            out[name] = filt
        return out

    def load_locations_and_location_tables_for_active_project(self):
        """Load Locations list and any existing location tables from the active project's DB."""
        if self._dm is None:
            try:
                self._dm = DataManager()
            except Exception:
                return
        pid = getattr(getattr(self, "_active_project", None), "id", None)
        if pid is None:
            return
        # Build locations list from per-project DB
        names: List[str] = []
        try:
            pr = self._dm.get_full_project_from_project_db(pid)
            if pr is not None:
                for loc in getattr(pr, "locations", []) or []:
                    try:
                        nm = getattr(loc, "name", None)
                        if nm:
                            names.append(str(nm))
                    except Exception:
                        continue
        except Exception:
            names = []
        self._locations_model.removeRows(0, self._locations_model.rowCount())
        for nm in sorted(set(names), key=lambda s: s.lower()):
            self._locations_model.appendRow(QStandardItem(nm))
        # Load existing location tables
        mapping = {}
        try:
            mapping = self._dm.get_location_tables_for_project(pid) or {}
        except Exception:
            mapping = {}
        self._location_tables_by_name = {str(k): (v or []) for k, v in mapping.items()}
        # Select first location if available
        try:
            if self._locations_model.rowCount() > 0:
                index = self._locations_model.index(0, 0)
                self.locations_list.setCurrentIndex(index)
                self._show_location_table_for(self._locations_model.item(0, 0).text())
            else:
                self._current_location_name = None
                self._populate_location_table_from_rows([])
        except Exception:
            pass

    # ----- Location Table row controls -----
    def _add_location_table_row(self):  # pragma: no cover - UI glue
        try:
            items = [QStandardItem(""), QStandardItem(""), QStandardItem("")]
            for it in items:
                it.setEditable(True)
            self._location_table_model.appendRow(items)
            # Select the new row
            r = self._location_table_model.rowCount() - 1
            idx = self._location_table_model.index(r, 0)
            try:
                self.location_table_view.setCurrentIndex(idx)
            except Exception:
                pass
            try:
                self.location_table_view.resizeColumnsToContents()
            except Exception:
                pass
        except Exception:
            pass

    def _delete_location_table_row(self):  # pragma: no cover - UI glue
        try:
            idx = self.location_table_view.currentIndex()
            if not idx.isValid():
                return
            self._location_table_model.removeRow(idx.row())
            try:
                self.location_table_view.resizeColumnsToContents()
            except Exception:
                pass
        except Exception:
            pass

    def _move_location_table_row_up(self):  # pragma: no cover - UI glue
        try:
            idx = self.location_table_view.currentIndex()
            if not idx.isValid():
                return
            row = idx.row()
            if row <= 0:
                return
            items = self._location_table_model.takeRow(row)
            self._location_table_model.insertRow(row - 1, items)
            try:
                new_idx = self._location_table_model.index(row - 1, idx.column())
                self.location_table_view.setCurrentIndex(new_idx)
            except Exception:
                pass
        except Exception:
            pass

    def _move_location_table_row_down(self):  # pragma: no cover - UI glue
        try:
            idx = self.location_table_view.currentIndex()
            if not idx.isValid():
                return
            row = idx.row()
            if row >= self._location_table_model.rowCount() - 1:
                return
            items = self._location_table_model.takeRow(row)
            self._location_table_model.insertRow(row + 1, items)
            try:
                new_idx = self._location_table_model.index(row + 1, idx.column())
                self.location_table_view.setCurrentIndex(new_idx)
            except Exception:
                pass
        except Exception:
            pass
