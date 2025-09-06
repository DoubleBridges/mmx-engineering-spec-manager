import types
from PySide6.QtCore import QObject, Signal

from mmx_engineering_spec_manager.controllers.projects_controller import ProjectsController


class _MockProjectsTab(QObject):
    open_project_signal = Signal(object)
    load_projects_signal = Signal()
    import_projects_signal = Signal()

    def display_projects(self, projects):
        pass


class _MockDetailView(QObject):
    save_button_clicked_signal = Signal(dict)

    def display_project(self, project):
        pass


def test_import_missing_settings_warning_gui_exception_fallback(mocker, capsys):
    dm = mocker.Mock()
    tab = _MockProjectsTab()
    detail = _MockDetailView()

    # Ensure settings are missing
    mocker.patch('mmx_engineering_spec_manager.controllers.projects_controller.get_settings', return_value=types.SimpleNamespace(innergy_base_url="", innergy_api_key=None))
    # Make QMessageBox.warning raise to exercise except branch
    mocker.patch('mmx_engineering_spec_manager.controllers.projects_controller.QMessageBox.warning', side_effect=RuntimeError('warn-fail'))

    ctrl = ProjectsController(dm, tab, detail)

    ctrl.import_from_innergy()

    out = capsys.readouterr().out
    assert "Missing Innergy settings" in out
