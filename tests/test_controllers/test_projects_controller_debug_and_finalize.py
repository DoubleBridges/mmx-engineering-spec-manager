import os
import json
import types
import pytest
from unittest.mock import Mock
from PySide6.QtCore import QObject, Signal

from mmx_engineering_spec_manager.controllers.projects_controller import ProjectsController


class _DummyWorker(QObject):
    progress = Signal(int)
    result = Signal(object)
    error = Signal(str)
    finished = Signal()


class _MockProjectsTab(QObject):
    open_project_signal = Signal(object)
    load_projects_signal = Signal()
    import_projects_signal = Signal()

    def __init__(self):
        super().__init__()
        self.logged_text = None

    def display_projects(self, projects):
        self._displayed = projects

    def display_log_text(self, text: str):
        # Used by debug/raw-response path
        self.logged_text = text


class _MockDetailView(QObject):
    save_button_clicked_signal = Signal(dict)

    def display_project(self, project):
        self._project = project


def test_import_debug_mode_shows_raw_payload(monkeypatch):
    # Enable debug mode to use raw path
    monkeypatch.setenv("DEBUG_SHOW_INNERGY_RESPONSE", "1")
    # Settings present
    monkeypatch.setattr(
        'mmx_engineering_spec_manager.controllers.projects_controller.get_settings',
        lambda: types.SimpleNamespace(innergy_base_url="https://app.innergy.com", innergy_api_key="K")
    )

    # Prepare mocks
    dm = Mock()
    dm.get_all_projects = lambda: []
    tab = _MockProjectsTab()
    detail = _MockDetailView()

    ctrl = ProjectsController(dm, tab, detail)

    # Patch run_in_thread to return a dummy worker and thread placeholder,
    # but also execute the provided function to cover the fetch_raw call.
    worker = _DummyWorker()
    def _rt_stub(func):
        _ = func()
        return (worker, object())
    monkeypatch.setattr(
        'mmx_engineering_spec_manager.controllers.projects_controller.run_in_thread',
        _rt_stub
    )

    # Monkeypatch InnergyImporter.get_projects_raw to return JSON content
    class _Importer:
        def get_projects_raw(self):
            return {"status_code": 200, "text": json.dumps({"Items": [{"Id": 1}]})}
    monkeypatch.setattr('mmx_engineering_spec_manager.controllers.projects_controller.InnergyImporter', _Importer)

    # Trigger import (debug path)
    ctrl.import_from_innergy()
    # Emit result to simulate completion of worker job (valid JSON)
    worker.result.emit({"status_code": 200, "text": json.dumps({"Items": [{"Id": 1}]})})
    # Emit again with invalid JSON to exercise the except branch (pretty-print fallback)
    worker.result.emit({"status_code": 200, "text": "not-json"})

    # Verify that log text was set on the projects tab
    assert tab.logged_text is not None
    assert "Status: 200" in tab.logged_text


def test_import_finalize_warning_and_info(monkeypatch):
    # Ensure debug mode is disabled for this test to exercise the normal path
    monkeypatch.setenv("DEBUG_SHOW_INNERGY_RESPONSE", "0")
    # Valid settings
    monkeypatch.setattr(
        'mmx_engineering_spec_manager.controllers.projects_controller.get_settings',
        lambda: types.SimpleNamespace(innergy_base_url="http://x", innergy_api_key="k")
    )

    dm = Mock()
    dm.get_all_projects = lambda: []
    tab = _MockProjectsTab()
    detail = _MockDetailView()

    ctrl = ProjectsController(dm, tab, detail)

    # Prepare worker
    worker = _DummyWorker()
    monkeypatch.setattr(
        'mmx_engineering_spec_manager.controllers.projects_controller.run_in_thread',
        lambda func: (worker, object())
    )

    # Patch QMessageBox to capture calls
    warnings = []
    infos = []
    monkeypatch.setattr('mmx_engineering_spec_manager.controllers.projects_controller.QMessageBox.warning', lambda *a, **k: warnings.append(True))
    monkeypatch.setattr('mmx_engineering_spec_manager.controllers.projects_controller.QMessageBox.information', lambda *a, **k: infos.append(True))

    # Case 1: imported_count == 0 -> warning
    ctrl.import_from_innergy()
    worker.result.emit(0)
    worker.finished.emit()
    assert warnings, "Expected warning dialog when 0 projects imported"

    # Reset for case 2 (>0) and run again
    warnings.clear(); infos.clear()
    ctrl.import_from_innergy()
    worker.result.emit(5)
    worker.finished.emit()
    assert infos, "Expected information dialog when projects imported"
