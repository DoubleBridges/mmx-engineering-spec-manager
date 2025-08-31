from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout

class ProjectsTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.load_button = QPushButton("Load Projects")
        self.layout.addWidget(self.load_button)