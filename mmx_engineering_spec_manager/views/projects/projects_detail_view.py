from PySide6.QtWidgets import QWidget, QFormLayout, QTabWidget, QVBoxLayout

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