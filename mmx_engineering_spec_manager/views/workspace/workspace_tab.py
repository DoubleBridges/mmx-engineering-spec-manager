from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel

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

        # Project label
        self.project_label = QLabel("No project loaded.")
        self.project_tab.setLayout(QVBoxLayout())
        self.project_tab.layout().addWidget(self.project_label)

        # Plan view (Locations)
        self.location_tab.setLayout(QVBoxLayout())
        self.plan_view = PlanViewWidget()
        self.location_tab.layout().addWidget(self.plan_view)

        # Elevation view (Wall)
        self.wall_tab.setLayout(QVBoxLayout())
        self.elevation_view = ElevationViewWidget()
        self.wall_tab.layout().addWidget(self.elevation_view)

    def set_view_model(self, view_model):
        """Attach a WorkspaceViewModel (optional, transitional).

        View remains operable without a VM; this enables MVVM binding without breaking legacy code.
        """
        try:
            self._vm = view_model
        except Exception:
            # Be resilient in tests/headless environments
            self._vm = None

    def display_project_data(self, project):
        """
        Receives project data and populates the workspace tabs.
        """
        self.current_project = project
        # Update label
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
