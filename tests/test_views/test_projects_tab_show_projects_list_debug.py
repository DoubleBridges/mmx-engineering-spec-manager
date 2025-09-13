import os
from mmx_engineering_spec_manager.views.projects.projects_tab import ProjectsTab


def test_show_projects_list_in_debug_mode(qtbot, monkeypatch):
    # Ensure debug flag is set before creating the tab
    monkeypatch.setenv("DEBUG_SHOW_INNERGY_RESPONSE", "1")

    tab = ProjectsTab()
    qtbot.addWidget(tab)

    # Enter details view then go back to list; this should exercise the debug branch
    tab.display_project_details(type("P", (), {"number": "1", "name": "N"})())
    tab.show_projects_list()

    # No assertions needed; this test ensures the debug branch executes without error
