from mmx_engineering_spec_manager.views.projects.projects_tab import ProjectsTab


def test_on_load_button_clicked_early_returns(qtbot):
    tab = ProjectsTab()
    qtbot.addWidget(tab)

    # No model set yet; selectionModel is None or has no selection
    tab.on_load_button_clicked()  # Should return without error

    # Now display projects but do not select anything
    class Dummy:
        def __init__(self, number, name, job_description=""):
            self.number = number
            self.name = name
            self.job_description = job_description

    tab.display_projects([Dummy("1", "A"), Dummy("2", "B")])
    tab.on_load_button_clicked()  # No selection -> early return without error
