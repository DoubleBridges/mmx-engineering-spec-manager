from PySide6.QtWidgets import QWidget, QTreeView, QVBoxLayout
from PySide6.QtGui import QStandardItemModel, QStandardItem


class WorkspaceTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.project_tree = QTreeView()
        self.layout.addWidget(self.project_tree)

    def open_project_in_workspace(self, project):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Name"])

        project_item = QStandardItem(getattr(project, "name", "Project"))

        locations = getattr(project, "locations", []) or []
        walls = getattr(project, "walls", []) or []
        products = getattr(project, "products", []) or []

        for location in locations:
            location_item = QStandardItem(getattr(location, "name", "Location"))

            if walls:
                for wall in walls:
                    wall_location_id = getattr(wall, "location_id", None)
                    location_id = getattr(location, "id", None)
                    if location_id is not None and wall_location_id != location_id:
                        continue

                    wall_item = QStandardItem(getattr(wall, "link_id", "Wall"))

                    if products:
                        for product in products:
                            product_wall_id = getattr(product, "wall_id", None)
                            wall_id = getattr(wall, "id", None)
                            if wall_id is not None and product_wall_id == wall_id:
                                product_item = QStandardItem(getattr(product, "name", "Product"))
                                wall_item.appendRow(product_item)

                    location_item.appendRow(wall_item)

            project_item.appendRow(location_item)

        model.appendRow(project_item)
        self.project_tree.setModel(model)