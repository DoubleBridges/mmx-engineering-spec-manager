from PySide6.QtCore import QObject, Slot, Signal


class ProjectsController(QObject):
    """
    Controller to manage the projects tab and project detail view.
    """
    project_opened_signal = Signal(object)

    def __init__(self, data_manager, projects_tab, projects_detail_view):
        super().__init__()
        self.data_manager = data_manager
        self.projects_tab = projects_tab
        self.projects_detail_view = projects_detail_view

        self._connect_signals()
        self.load_projects()

    def _connect_signals(self):
        self.projects_tab.load_projects_signal.connect(self.load_projects)
        self.projects_tab.open_project_signal.connect(self.open_project)
        self.projects_detail_view.save_button_clicked_signal.connect(self.save_project)

    @Slot()
    def load_projects(self):
        """Loads all projects from the data manager and displays them in the projects tab."""
        projects = self.data_manager.get_all_projects()
        self.projects_tab.display_projects(projects)

    @Slot(object)
    def open_project(self, project):
        """Opens a project and displays its details in the project detail view."""
        detailed_project = self.data_manager.get_project_by_id(project.id)
        self.projects_detail_view.display_project(detailed_project)
        self.project_opened_signal.emit(detailed_project)

    @Slot(dict)
    def save_project(self, project_data):
        """Saves project data and refreshes the project list."""
        self.data_manager.save_project(project_data)
        self.load_projects()