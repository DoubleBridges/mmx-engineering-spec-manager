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