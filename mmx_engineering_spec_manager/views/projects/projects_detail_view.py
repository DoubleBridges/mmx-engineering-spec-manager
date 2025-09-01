from PySide6.QtWidgets import QWidget, QFormLayout, QTabWidget, QVBoxLayout, QLabel


class ProjectsDetailView(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Create the form layout for project properties
        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)

        # Create the tab widget for collections
        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

    def display_project(self, project):
        # Clear the existing layout
        while self.form_layout.rowCount() > 0:
            self.form_layout.removeRow(0)

        # Add the project's properties to the form layout
        self.form_layout.addRow("Number:", QLabel(project.number))
        self.form_layout.addRow("Name:", QLabel(project.name))
        self.form_layout.addRow("Job Description:", QLabel(project.job_description))

        # This will be used later to display collections
        self.current_project = project