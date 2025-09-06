from PySide6.QtWidgets import QApplication

from mmx_engineering_spec_manager.views.projects.projects_tab import ProjectsTab


def test_projects_tab_second_third_columns_resized(qtbot, monkeypatch):
    # Ensure debug mode is off so table is shown
    monkeypatch.delenv("DEBUG_SHOW_INNERGY_RESPONSE", raising=False)

    tab = ProjectsTab()
    qtbot.addWidget(tab)

    # Provide a couple of dummy projects with minimal attributes
    class P:
        def __init__(self, number, name, jd):
            self.number = number
            self.name = name
            self.job_description = jd

    projects = [P("P-1", "Name1", "Desc1"), P("P-2", "Name2", "Desc2")]

    tab.display_projects(projects)

    header = tab.projects_table.horizontalHeader()
    # Baseline hint size for columns 1 and 2
    hint1 = header.sectionSizeHint(1)
    hint2 = header.sectionSizeHint(2)
    # Actual sizes applied should be at least 3x of the hint
    assert header.sectionSize(1) >= 3 * hint1
    assert header.sectionSize(2) >= 3 * hint2
