from PySide6.QtCore import QObject, Signal

from mmx_engineering_spec_manager.controllers.projects_controller import ProjectsController


class _TabWithDetails(QObject):
    open_project_signal = Signal(object)
    import_projects_signal = Signal()

    def __init__(self):
        super().__init__()
        self.shown = None

    def display_projects(self, projects):
        pass

    def display_project_details(self, project):
        self.shown = project


class _DetailView(QObject):
    save_button_clicked_signal = Signal(dict)

    def __init__(self):
        super().__init__()
        self.project = None

    def display_project(self, project):
        self.project = project


class _DM:
    def __init__(self, project):
        self._p = project

    def get_all_projects(self):
        return []

    def get_project_by_id(self, _id):
        return self._p

    def save_project(self, data):
        pass


class _P:
    def __init__(self, pid=1):
        self.id = pid
        self.number = "N"
        self.name = "Proj"


def test_open_project_calls_display_project_details_when_available(mocker):
    proj = _P(7)
    dm = _DM(proj)
    tab = _TabWithDetails()
    detail = _DetailView()

    ctrl = ProjectsController(dm, tab, detail)

    ctrl.open_project(proj)

    # Should have displayed in both the detail view and the tab swapper
    assert detail.project is proj
    assert tab.shown is proj
