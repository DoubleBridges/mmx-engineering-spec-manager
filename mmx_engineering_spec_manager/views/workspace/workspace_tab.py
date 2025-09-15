from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel, QPushButton, QHBoxLayout

from .plan_view import PlanViewWidget
from .elevation_view import ElevationViewWidget


class WorkspaceTab(QWidget):
    """
    The main widget for the 'Workspace' tab.
    It contains its own tab widget for different levels of detail.
    """
    def __init__(self):
        super().__init__()
        self._vm = None  # Optional WorkspaceViewModel (transitional wiring)
        self._pending_changes: dict = {}
        self.layout = QVBoxLayout(self)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.project_tab = QWidget()
        self.location_tab = QWidget()
        self.wall_tab = QWidget()
        self.product_tab = QWidget()

        self.tab_widget.addTab(self.project_tab, "Project")
        self.tab_widget.addTab(self.location_tab, "Locations")
        self.tab_widget.addTab(self.wall_tab, "Wall")
        self.tab_widget.addTab(self.product_tab, "Product")

        self.current_project = None

        # Project area: label + Save button row
        self.project_tab.setLayout(QVBoxLayout())
        header_row = QHBoxLayout()
        self.project_label = QLabel("No project loaded.")
        header_row.addWidget(self.project_label)
        header_row.addStretch(1)
        self.btn_save = QPushButton("Save Workspace")
        try:
            self.btn_save.clicked.connect(self._on_save_clicked)
        except Exception:
            pass
        header_row.addWidget(self.btn_save)
        self.project_tab.layout().addLayout(header_row)

        # Plan view (Locations)
        self.location_tab.setLayout(QVBoxLayout())
        self.plan_view = PlanViewWidget()
        self.location_tab.layout().addWidget(self.plan_view)
        # Connect movement signal to mark dirty and collect changes
        try:
            self.plan_view.productMoved.connect(self._on_plan_product_moved)
        except Exception:
            pass

        # Elevation view (Wall)
        self.wall_tab.setLayout(QVBoxLayout())
        self.elevation_view = ElevationViewWidget()
        self.wall_tab.layout().addWidget(self.elevation_view)
        try:
            self.elevation_view.productMoved.connect(self._on_elevation_product_moved)
        except Exception:
            pass

    def set_view_model(self, view_model):
        """Attach a WorkspaceViewModel (optional, transitional).

        View remains operable without a VM; this enables MVVM binding without breaking legacy code.
        """
        try:
            self._vm = view_model
            # Subscribe to VM events so the View renders from VM state when available
            try:
                if hasattr(self._vm, "tree_loaded"):
                    self._vm.tree_loaded.subscribe(self._on_tree_loaded)
            except Exception:
                pass
            try:
                # Notifications can be used later for toast/messages; ignored for now
                if hasattr(self._vm, "notification"):
                    self._vm.notification.subscribe(lambda _p: None)
            except Exception:
                pass
            # If a project is already displayed, let the VM know and trigger a load
            try:
                if self.current_project is not None and hasattr(self._vm, "set_active_project"):
                    self._vm.set_active_project(self.current_project)
                    if hasattr(self._vm, "load"):
                        self._vm.load()
            except Exception:
                pass
        except Exception:
            # Be resilient in tests/headless environments
            self._vm = None

    def _on_tree_loaded(self, tree: dict):  # pragma: no cover - thin glue
        try:
            self._render_tree(tree or {})
        except Exception:
            pass

    def _render_tree(self, tree: dict) -> None:
        """Render Workspace UI from a VM-provided tree dict.

        Currently updates the Project label from tree['label'] when present. More bindings can be added later.
        """
        try:
            label = None
            if isinstance(tree, dict):
                label = tree.get("label")
            if label:
                self.project_label.setText(f"Project Loaded: {label}")
        except Exception:
            pass

    def display_project_data(self, project):
        """
        Receives project data and populates the workspace tabs.
        """
        self.current_project = project
        # Update label (legacy path; VM-based rendering will override when available)
        self.project_label.setText(f"Project Loaded: {project.name} ({project.number})")
        # Initialize default scenes (safe defaults; actual data wiring will be added later)
        try:
            # If project has at least one wall, use its dimensions
            walls = getattr(project, "walls", []) or []
            if walls:
                w = walls[0]
                self.plan_view.set_wall(length_in=getattr(w, "width", 120.0), thickness_in=getattr(w, "thicknesses", 4.0) or 4.0)
                self.elevation_view.set_wall(length_in=getattr(w, "width", 120.0), height_in=getattr(w, "height", 96.0) or 96.0)
            else:
                self.plan_view.set_wall()
                self.elevation_view.set_wall()
        except Exception:
            # In tests/mocks without full attributes, fall back to defaults
            self.plan_view.set_wall()
            self.elevation_view.set_wall()
        # Reset pending changes on new project
        self._pending_changes = {}
        # If a VM is attached, reflect the project selection into the VM and ask it to load its state
        try:
            if self._vm is not None:
                if hasattr(self._vm, "set_active_project"):
                    self._vm.set_active_project(project)
                if hasattr(self._vm, "load"):
                    self._vm.load()
        except Exception:
            pass

    # ---- Dirty tracking and save wiring ----
    def _on_plan_product_moved(self, product_id: int, x_left: float, y_from_face: float):  # pragma: no cover - thin UI glue
        try:
            self._pending_changes.setdefault("plan_moves", []).append({
                "product_id": int(product_id),
                "x_left": float(x_left),
                "y_from_face": float(y_from_face),
            })
        except Exception:
            pass
        self._mark_dirty()

    def _on_elevation_product_moved(self, product_id: int, x_origin_from_right: float, z_origin_from_bottom: float):  # pragma: no cover - thin UI glue
        try:
            self._pending_changes.setdefault("elevation_moves", []).append({
                "product_id": int(product_id),
                "x_origin_from_right": float(x_origin_from_right),
                "z_origin_from_bottom": float(z_origin_from_bottom),
            })
        except Exception:
            pass
        self._mark_dirty()

    def _mark_dirty(self):  # pragma: no cover - thin UI glue
        try:
            if self._vm is not None and hasattr(self._vm, "mark_dirty"):
                self._vm.mark_dirty(True)
        except Exception:
            pass

    def _on_save_clicked(self):  # pragma: no cover - thin UI glue
        try:
            if self._vm is None or not hasattr(self._vm, "save_changes"):
                return
            ok = self._vm.save_changes(self._pending_changes or {})
            if ok:
                # Clear pending changes and mark clean
                self._pending_changes = {}
                try:
                    if hasattr(self._vm, "mark_dirty"):
                        self._vm.mark_dirty(False)
                except Exception:
                    pass
        except Exception:
            # Non-fatal in UI
            pass
