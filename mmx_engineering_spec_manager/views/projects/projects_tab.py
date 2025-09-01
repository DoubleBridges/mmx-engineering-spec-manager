from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QTableView
from PySide6.QtCore import Signal, QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem


class ProjectsTab(QWidget):
    load_projects_signal = Signal()
    open_project_signal = Signal(object)

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.load_button = QPushButton("Load Projects")
        self.layout.addWidget(self.load_button)

        # Connect the button click to our custom signal
        self.load_button.clicked.connect(self.load_projects_signal.emit)

        # Add a QTableView to display the projects
        self.projects_table = QTableView()
        self.layout.addWidget(self.projects_table)

        # Connect the table's double-click signal to our handler
        self.projects_table.doubleClicked.connect(self.on_project_double_clicked)

        self.projects = []

    def display_projects(self, projects):
        self.projects = projects
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Number", "Name", "Job Description"])

        for project in self.projects:
            number_item = QStandardItem(project.number)
            name_item = QStandardItem(project.name)
            description_item = QStandardItem(project.job_description)
            model.appendRow([number_item, name_item, description_item])

        self.projects_table.setModel(model)

    def on_project_double_clicked(self, index: QModelIndex):
        if index.isValid():
            project_index = index.row()
            project = self.projects[project_index]
            self.open_project_signal.emit(project)

    def display_project_details(self, project):
        # This method will be used to display the project's details
        # For now, we'll just store the project in an instance variable
        self.current_project = project