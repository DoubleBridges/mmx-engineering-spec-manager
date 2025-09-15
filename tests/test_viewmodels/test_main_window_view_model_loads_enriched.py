import types
import os

import pytest

from mmx_engineering_spec_manager.viewmodels import MainWindowViewModel
from mmx_engineering_spec_manager.services import Result


class DummyProject:
    def __init__(self, pid, number=None):
        self.id = pid
        self.number = number


def test_vm_uses_bootstrap_service_to_load_enriched_when_db_exists(monkeypatch, tmp_path):
    # Arrange: simulate existing per-project DB
    fake_db = tmp_path / "p.sqlite"
    fake_db.write_text("")

    # Monkeypatch the VM module's db path helper and os.path.exists
    import mmx_engineering_spec_manager.viewmodels.main_window_view_model as vm_mod

    def fake_db_path(_project):
        return str(fake_db)

    monkeypatch.setattr(vm_mod, "project_sqlite_db_path", fake_db_path, raising=False)

    # Create a dummy bootstrap service that returns an enriched project
    calls = {"ensure": [], "load": []}

    enriched = object()

    class DummyService:
        def ensure_project_db(self, project):
            calls["ensure"].append(getattr(project, "id", None))
            return Result.ok_value(None)

        def load_enriched_project(self, project):
            calls["load"].append(getattr(project, "id", None))
            return Result.ok_value(enriched)

    vm = MainWindowViewModel(data_manager=types.SimpleNamespace(), project_bootstrap_service=DummyService())

    # Subscribe to opened event
    opened = {"project": None}

    def on_opened(p):
        opened["project"] = p

    vm.project_opened.subscribe(on_opened)

    # Act
    p = DummyProject(pid=7, number=None)  # number None to avoid ingestion branch
    vm.set_active_project(p)

    # Assert
    assert calls["ensure"] == [7]
    assert calls["load"] == [7]
    assert opened["project"] is enriched


def test_vm_emits_warning_and_original_project_when_load_fails(monkeypatch, tmp_path):
    # Arrange: existing DB path
    fake_db = tmp_path / "p.sqlite"
    fake_db.write_text("")

    import mmx_engineering_spec_manager.viewmodels.main_window_view_model as vm_mod

    def fake_db_path(_project):
        return str(fake_db)

    monkeypatch.setattr(vm_mod, "project_sqlite_db_path", fake_db_path, raising=False)

    notifications = []

    class DummyService:
        def ensure_project_db(self, project):
            return Result.ok_value(None)

        def load_enriched_project(self, project):
            return Result.fail("boom")

    vm = MainWindowViewModel(data_manager=types.SimpleNamespace(), project_bootstrap_service=DummyService())
    vm.notification.subscribe(lambda p: notifications.append(p))

    opened = {"project": None}
    vm.project_opened.subscribe(lambda p: opened.__setitem__("project", p))

    # Act
    p = DummyProject(pid=11, number=None)
    vm.set_active_project(p)

    # Assert: original project emitted and a warning notification present
    assert opened["project"] is p
    assert any(n.get("level") == "warning" for n in notifications)
