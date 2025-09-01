from PySide6.QtCore import QObject


class MainWindowController(QObject):
    def __init__(self, main_window, data_manager):
        super().__init__()
        self.main_window = main_window
        self.data_manager = data_manager

        self.main_window.window_ready_signal.connect(self.initialize)
        self.connect_projects_detail_view(self.main_window.projects_detail_view)

    def initialize(self):
        self.connect_projects_tab(self.main_window.projects_tab)
        self.load_projects()

    def connect_projects_tab(self, projects_tab):
        projects_tab.load_projects_signal.connect(self.load_projects)
        projects_tab.open_project_signal.connect(self.open_project)

    def connect_projects_detail_view(self, projects_detail_view):
        projects_detail_view.save_button_clicked_signal.connect(self.save_project)

    def load_projects(self):
        projects = self.data_manager.get_all_projects()
        self.main_window.projects_tab.display_projects(projects)

    def open_project(self, project):
        project = self.data_manager.get_project_by_id(project.id)
        self.main_window.projects_detail_view.display_project(project)

    def save_project(self, project_data):
        self.data_manager.save_project(project_data)