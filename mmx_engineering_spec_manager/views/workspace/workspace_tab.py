from PySide6.QtWidgets import QWidget, QTreeView, QVBoxLayout
from PySide6.QtGui import QStandardItemModel, QStandardItem


class WorkspaceTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.project_tree = QTreeView()
        self.layout.addWidget(self.project_tree)

    def display_project(self, project):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Name"])

        project_item = QStandardItem(project.name)

        for location in project.locations:
            location_item = QStandardItem(location.name)
            project_item.appendRow(location_item)

        model.appendRow(project_item)
        self.project_tree.setModel(model)