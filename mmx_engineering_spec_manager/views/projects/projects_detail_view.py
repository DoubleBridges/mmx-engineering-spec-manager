from PySide6.QtWidgets import QWidget, QFormLayout, QTabWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Signal


class ProjectsDetailView(QWidget):
    save_button_clicked_signal = Signal(object)

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

        # Create the save button
        self.save_button = QPushButton("Save")
        self.layout.addWidget(self.save_button)

        # Connect the button click to our custom signal
        self.save_button.clicked.connect(self.on_save_button_clicked)

        self.current_project = None

    def open_project_details(self, project):
        # Clear the existing layout
        while self.form_layout.rowCount() > 0:
            self.form_layout.removeRow(0)

        # Add the project's properties to the form layout
        self.form_layout.addRow("Number:", QLineEdit(project.number))
        self.form_layout.addRow("Name:", QLineEdit(project.name))
        self.form_layout.addRow("Job Description:", QLineEdit(project.job_description))

        # Clear the existing tabs
        self.tab_widget.clear()

        # Add tabs for each collection
        if project.locations:
            locations_tab = QWidget()
            self.tab_widget.addTab(locations_tab, "Locations")

        if project.products:
            products_tab = QWidget()
            self.tab_widget.addTab(products_tab, "Products")

        if project.walls:
            walls_tab = QWidget()
            self.tab_widget.addTab(walls_tab, "Walls")

        if project.custom_fields:
            custom_fields_tab = QWidget()
            self.tab_widget.addTab(custom_fields_tab, "Custom Fields")

        if project.specification_groups:
            spec_groups_tab = QWidget()
            self.tab_widget.addTab(spec_groups_tab, "Specification Groups")

        if project.global_prompts:
            global_prompts_tab = QWidget()
            self.tab_widget.addTab(global_prompts_tab, "Global Prompts")

        if project.wizard_prompts:
            wizard_prompts_tab = QWidget()
            self.tab_widget.addTab(wizard_prompts_tab, "Wizard Prompts")

        self.current_project = project

    def on_save_button_clicked(self):
        # This will be used to get the data from the form
        updated_data = self.get_data()
        self.save_button_clicked_signal.emit(updated_data)

    def get_data(self):
        # This will be used to get the data from the form
        return {
            "number": self.form_layout.itemAt(0, QFormLayout.ItemRole.FieldRole).widget().text(),
            "name": self.form_layout.itemAt(1, QFormLayout.ItemRole.FieldRole).widget().text(),
            "job_description": self.form_layout.itemAt(2, QFormLayout.ItemRole.FieldRole).widget().text()
        }