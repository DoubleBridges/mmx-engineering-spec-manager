import types
import pytest
from PySide6.QtCore import QObject, Signal

from mmx_engineering_spec_manager.controllers.projects_controller import ProjectsController


class _MockProjectsTab(QObject):
    open_project_signal = Signal(object)
    load_projects_signal = Signal()
    # Include import signal as in real tab
    import_projects_signal = Signal()

    def display_projects(self, projects):
        self._displayed = projects


class _MockDetailView(QObject):
    save_button_clicked_signal = Signal(dict)

    def display_project(self, project):
        self._project = project


def test_import_from_innergy_missing_settings_shows_warning_and_aborts(mocker):
    # Patch settings to simulate missing key/base URL
    mocker.patch('mmx_engineering_spec_manager.controllers.projects_controller.get_settings', return_value=types.SimpleNamespace(innergy_base_url="", innergy_api_key=None))
    # Patch QMessageBox.warning to avoid GUI and capture calls
    warning = mocker.patch('mmx_engineering_spec_manager.controllers.projects_controller.QMessageBox.warning')

    dm = mocker.Mock()
    tab = _MockProjectsTab()
    detail = _MockDetailView()

    ctrl = ProjectsController(dm, tab, detail)

    # Trigger import
    ctrl.import_from_innergy()

    warning.assert_called_once()
    # Ensure background import was not started
    assert not dm.sync_projects_from_innergy.called


def test_on_import_error_shows_critical_popup(mocker):
    # Controller with minimal mocks
    dm = mocker.Mock()
    tab = _MockProjectsTab()
    detail = _MockDetailView()

    ctrl = ProjectsController(dm, tab, detail)

    critical = mocker.patch('mmx_engineering_spec_manager.controllers.projects_controller.QMessageBox.critical')

    # Invoke the error slot directly (simulating worker error)
    ctrl._on_import_error("boom")

    critical.assert_called_once()
