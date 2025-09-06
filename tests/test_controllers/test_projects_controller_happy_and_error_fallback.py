import types
import pytest
from PySide6.QtCore import QObject, Signal

from mmx_engineering_spec_manager.controllers.projects_controller import ProjectsController


class _DummyWorker(QObject):
    result = Signal(object)
    error = Signal(str)
    finished = Signal()


class _MockProjectsTab(QObject):
    open_project_signal = Signal(object)
    load_projects_signal = Signal()
    import_projects_signal = Signal()

    def display_projects(self, projects):
        self._displayed = projects


class _MockDetailView(QObject):
    save_button_clicked_signal = Signal(dict)

    def display_project(self, project):
        self._project = project


def test_import_happy_path_wires_worker_and_triggers_reload(mocker):
    # Valid settings
    mocker.patch('mmx_engineering_spec_manager.controllers.projects_controller.get_settings', return_value=types.SimpleNamespace(innergy_base_url="http://x", innergy_api_key="k"))

    dm = mocker.Mock()
    tab = _MockProjectsTab()
    detail = _MockDetailView()

    ctrl = ProjectsController(dm, tab, detail)

    # Patch run_in_thread to return our dummy worker + thread placeholder
    worker = _DummyWorker()
    run = mocker.patch('mmx_engineering_spec_manager.controllers.projects_controller.run_in_thread', return_value=(worker, object()))

    # Spy on load_projects to ensure it's connected
    spy_reload = mocker.spy(ctrl, 'load_projects')

    # Invoke import
    ctrl.import_from_innergy()

    # Ensure run_in_thread called with dm.sync_projects_from_innergy
    run.assert_called_once()

    # Emit finished to simulate completion, should trigger reload
    worker.finished.emit()

    # load_projects should have been called at least once from completion
    assert spy_reload.call_count >= 1


def test_on_import_error_gui_exception_fallback_prints(mocker, capsys):
    dm = mocker.Mock()
    tab = _MockProjectsTab()
    detail = _MockDetailView()

    ctrl = ProjectsController(dm, tab, detail)

    # Make QMessageBox.critical raise to enter except branch
    mocker.patch('mmx_engineering_spec_manager.controllers.projects_controller.QMessageBox.critical', side_effect=RuntimeError('GUI-fail'))

    ctrl._on_import_error("err-msg")

    out = capsys.readouterr().out
    assert "Import error:" in out
