from PySide6.QtCore import QObject


class MainWindowController(QObject):
    def __init__(self, main_window, data_manager):
        super().__init__()
        self.main_window = main_window
        self.data_manager = data_manager

        self.connect_projects_tab(main_window.projects_tab)

    def connect_projects_tab(self, projects_tab):
        projects_tab.load_projects_signal.connect(self.load_projects)
        projects_tab.open_project_signal.connect(self.open_project)

    def load_projects(self):
        projects = self.data_manager.get_all_projects()
        self.main_window.projects_tab.display_projects(projects)

    def open_project(self, project):
        # Placeholder for opening a project in the UI
        print(f"Opening project: {project.name}")