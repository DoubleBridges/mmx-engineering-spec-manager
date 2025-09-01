import pytest
from PySide6.QtWidgets import QFormLayout, QTabWidget
from mmx_engineering_spec_manager.views.projects.projects_detail_view import ProjectsDetailView

def test_projects_detail_view_has_form_and_tabs(qtbot):
    """
    Test that the ProjectsDetailView has a QFormLayout and a QTabWidget.
    """
    projects_detail_view = ProjectsDetailView()
    qtbot.addWidget(projects_detail_view)

    # Assert that a QFormLayout exists
    form_layout = projects_detail_view.findChild(QFormLayout)
    assert form_layout is not None

    # Assert that a QTabWidget exists
    tab_widget = projects_detail_view.findChild(QTabWidget)
    assert tab_widget is not None