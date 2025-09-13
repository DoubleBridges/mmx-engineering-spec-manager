from PySide6.QtCore import Qt

from mmx_engineering_spec_manager.views.projects.projects_tab import ProjectsTab


class DummyProj:
    def __init__(self, number, name, job_description=""):
        self.number = number
        self.name = name
        self.job_description = job_description


def test_projects_tab_load_button_emits_selected_project(qtbot):
    tab = ProjectsTab()
    qtbot.addWidget(tab)

    # Provide projects
    projs = [DummyProj("P-1", "Alpha"), DummyProj("P-2", "Beta")]
    tab.display_projects(projs)

    # Select second row, first column
    view = tab.projects_table
    model = view.model()
    index = model.index(1, 0)
    view.setCurrentIndex(index)
    view.selectRow(1)

    # Capture signal
    captured = {}
    def on_open(p):
        captured['p'] = p
    tab.open_project_signal.connect(on_open)

    # Click load
    qtbot.mouseClick(tab.load_button, Qt.LeftButton)

    assert captured.get('p') is projs[1]


def test_projects_tab_double_click_emits_project(qtbot):
    tab = ProjectsTab()
    qtbot.addWidget(tab)

    projs = [DummyProj("P-1", "Alpha")]
    tab.display_projects(projs)

    view = tab.projects_table
    model = view.model()
    idx = model.index(0, 0)

    captured = {}
    tab.open_project_signal.connect(lambda p: captured.setdefault('p', p))

    # Simulate double click
    # Directly call slot for simplicity
    tab.on_project_double_clicked(idx)

    assert captured.get('p') is projs[0]
