import pytest
from PySide6.QtWidgets import QPushButton
from mmx_engineering_spec_manager.views.projects.projects_tab import ProjectsTab

def test_projects_tab_has_load_button(qtbot):
    """
    Test that the ProjectsTab has a 'Load Projects' button.
    """
    projects_tab = ProjectsTab()
    qtbot.addWidget(projects_tab)

    load_button = projects_tab.findChild(QPushButton)
    assert load_button is not None
    assert load_button.text() == "Load Projects"