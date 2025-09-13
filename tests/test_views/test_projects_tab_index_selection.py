from mmx_engineering_spec_manager.views.projects.projects_tab import ProjectsTab


class Dummy:
    def __init__(self, number, name, job_description=""):
        self.number = number
        self.name = name
        self.job_description = job_description


def test_on_load_button_clicked_selected_indexes_branch(qtbot):
    tab = ProjectsTab()
    qtbot.addWidget(tab)

    projs = [Dummy("1", "A"), Dummy("2", "B")]
    tab.display_projects(projs)

    # Select a single cell (no selectedRows), should fall back to selectedIndexes path
    index = tab.projects_table.model().index(0, 1)
    tab.projects_table.setCurrentIndex(index)

    captured = {}
    tab.open_project_signal.connect(lambda p: captured.setdefault('p', p))

    tab.on_load_button_clicked()

    assert captured.get('p') is projs[0]
