import types
from PySide6.QtCore import QObject, Signal

from mmx_engineering_spec_manager.controllers.projects_controller import ProjectsController


class _DummyWorker(QObject):
    result = Signal(object)
    error = Signal(str)
    finished = Signal()
    progress = Signal(int)


class _DummyDialog:
    def __init__(self, *a, **k):
        self.closed = False
    def setWindowTitle(self, t):
        pass
    def setAutoClose(self, v):
        pass
    def setAutoReset(self, v):
        pass
    def setValue(self, v):
        pass
    def setMinimumDuration(self, v):
        pass
    def show(self):
        pass
    def close(self):
        self.closed = True


class _Tab(QObject):
    open_project_signal = Signal(object)
    load_projects_signal = Signal()
    import_projects_signal = Signal()
    def display_projects(self, projects):
        self._projects = projects


class _Detail(QObject):
    save_button_clicked_signal = Signal(dict)
    def display_project(self, project):
        self._p = project


def test_on_import_error_closes_progress_dialog_if_present(monkeypatch):
    monkeypatch.setattr(
        'mmx_engineering_spec_manager.controllers.projects_controller.get_settings',
        lambda: types.SimpleNamespace(innergy_base_url='http://x', innergy_api_key='k')
    )

    last_dialog = {}
    def _new_dialog(*a, **k):
        d = _DummyDialog()
        last_dialog['dlg'] = d
        return d
    monkeypatch.setattr(
        'mmx_engineering_spec_manager.controllers.projects_controller.QProgressDialog',
        _new_dialog
    )

    dm = types.SimpleNamespace(get_all_projects=lambda: [], sync_projects_from_innergy=lambda **k: None, get_project_by_id=lambda _id: None, save_project=lambda d: None)
    tab = _Tab(); detail = _Detail()
    ctrl = ProjectsController(dm, tab, detail)

    # Stub run_in_thread to avoid real threading and provide a worker with required signals
    monkeypatch.setattr('mmx_engineering_spec_manager.controllers.projects_controller.run_in_thread', lambda func: (_DummyWorker(), object()))

    # Start import to create progress dialog
    ctrl.import_from_innergy()
    # Now trigger error; should attempt to close the dialog
    ctrl._on_import_error('boom')

    assert 'dlg' in last_dialog and last_dialog['dlg'].closed is True
