from mmx_engineering_spec_manager.views.projects.projects_tab import ProjectsTab


class DummyProj:
    def __init__(self, number="N-1", name="Name", job_description="Desc"):
        self.number = number
        self.name = name
        self.job_description = job_description


def test_show_projects_list_restores_list_view_and_controls(qtbot):
    tab = ProjectsTab()
    qtbot.addWidget(tab)

    # First go into details mode
    tab.display_project_details(DummyProj())

    # Now return to the list
    tab.show_projects_list()

    # The details view should now be hidden and the select-another button hidden
    assert not tab.projects_detail_view.isVisible()
    assert not tab.select_another_button.isVisible()
    # The current project context should be cleared
    assert tab.current_project is None
