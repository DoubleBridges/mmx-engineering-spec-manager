from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QLabel


class WorkspaceTab(QWidget):
    """
    The main widget for the 'Workspace' tab.
    It contains its own tab widget for different levels of detail.
    """
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.project_tab = QWidget()
        self.wall_tab = QWidget()
        self.product_tab = QWidget()

        self.tab_widget.addTab(self.project_tab, "Project")
        self.tab_widget.addTab(self.wall_tab, "Wall")
        self.tab_widget.addTab(self.product_tab, "Product")

        self.current_project = None

        # Add a label to show which project is loaded
        self.project_label = QLabel("No project loaded.")
        self.project_tab.setLayout(QVBoxLayout())
        self.project_tab.layout().addWidget(self.project_label)

    def display_project_data(self, project):
        """
        Receives project data and populates the workspace tabs.
        """
        self.current_project = project
        self.project_label.setText(f"Project Loaded: {project.name} ({project.number})")
