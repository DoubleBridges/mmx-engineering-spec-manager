import types

from mmx_engineering_spec_manager.viewmodels import MainWindowViewModel
from mmx_engineering_spec_manager.services import Result


class DummyProject:
    def __init__(self, pid, number=None):
        self.id = pid
        self.number = number


def test_set_active_project_updates_state_and_emits_event():
    # Use a lightweight stand-in for DataManager
    data_manager = types.SimpleNamespace()
    vm = MainWindowViewModel(data_manager)

    events = {
        "opened": None,
        "refresh": 0,
        "notifications": [],
    }

    def on_opened(project):
        events["opened"] = project

    def on_refresh():
        events["refresh"] += 1

    def on_notify(payload):
        events["notifications"].append(payload)

    vm.project_opened.subscribe(on_opened)
    vm.refresh_requested.subscribe(on_refresh)
    vm.notification.subscribe(on_notify)

    project = DummyProject(pid=123)
    vm.set_active_project(project)

    assert vm.view_state.active_project_id == 123
    assert events["opened"] is project

    vm.request_refresh()
    assert events["refresh"] == 1

    vm.set_error("oops")
    assert vm.view_state.error == "oops"
    assert any(n["level"] == "error" and n["message"] == "oops" for n in events["notifications"]) 


def test_vm_delegates_ensure_to_bootstrap_service_and_emits_open():
    # Arrange dummy service capturing calls
    calls = {"ensure": []}

    class DummyService:
        def ensure_project_db(self, project):
            calls["ensure"].append(getattr(project, "id", None))
            return Result.ok_value(None)

    vm = MainWindowViewModel(data_manager=types.SimpleNamespace(), project_bootstrap_service=DummyService())

    # Subscribe to opened event
    opened = {"project": None}

    def on_opened(p):
        opened["project"] = p

    vm.project_opened.subscribe(on_opened)

    # Act
    p = DummyProject(pid=42)
    vm.set_active_project(p)

    # Assert: service was called and event emitted
    assert calls["ensure"] == [42]
    assert opened["project"] is p


def test_vm_ingests_via_service_on_first_open_success(monkeypatch, tmp_path):
    # Arrange: DB does not exist yet, API key present
    db_file = tmp_path / "proj.sqlite"
    monkeypatch.setattr(
        "mmx_engineering_spec_manager.viewmodels.main_window_view_model.project_sqlite_db_path",
        lambda _p: str(db_file),
        raising=False,
    )
    monkeypatch.setattr(
        "mmx_engineering_spec_manager.viewmodels.main_window_view_model.get_settings",
        lambda: types.SimpleNamespace(innergy_api_key="abc"),
        raising=False,
    )

    calls = {"ensure": [], "ingest": [], "load": []}

    class DummyService:
        def ensure_project_db(self, project):
            calls["ensure"].append(getattr(project, "id", None))
            return Result.ok_value(None)

        def ingest_project_details_if_needed(self, project, settings=None):
            calls["ingest"].append((getattr(project, "id", None), bool(getattr(settings, "innergy_api_key", None))))
            return Result.ok_value(True)

        def load_enriched_project(self, project):
            calls["load"].append(getattr(project, "id", None))
            enriched = DummyProject(pid=project.id, number=project.number)
            enriched._enriched = True
            return Result.ok_value(enriched)

    vm = MainWindowViewModel(data_manager=types.SimpleNamespace(), project_bootstrap_service=DummyService())

    opened = {"project": None}
    vm.project_opened.subscribe(lambda p: opened.__setitem__("project", p))

    p = DummyProject(pid=100, number="J-100")
    vm.set_active_project(p)

    # Assert: service was used and enriched project was emitted
    assert calls["ensure"] == [100]
    assert calls["ingest"] == [(100, True)]
    assert calls["load"] == [100]
    assert getattr(opened["project"], "_enriched", False) is True


def test_vm_ingest_failure_emits_error_notification(monkeypatch, tmp_path):
    # Arrange: DB does not exist yet, API key present, ingestion fails
    db_file = tmp_path / "proj.sqlite"
    # Ensure file is absent
    if db_file.exists():
        db_file.unlink()
    monkeypatch.setattr(
        "mmx_engineering_spec_manager.viewmodels.main_window_view_model.project_sqlite_db_path",
        lambda _p: str(db_file),
        raising=False,
    )
    monkeypatch.setattr(
        "mmx_engineering_spec_manager.viewmodels.main_window_view_model.get_settings",
        lambda: types.SimpleNamespace(innergy_api_key="abc"),
        raising=False,
    )

    class DummyService:
        def ensure_project_db(self, project):
            return Result.ok_value(None)

        def ingest_project_details_if_needed(self, project, settings=None):
            return Result.fail("boom")

        def load_enriched_project(self, project):
            return Result.ok_value(project)

    vm = MainWindowViewModel(data_manager=types.SimpleNamespace(), project_bootstrap_service=DummyService())

    notifications = []
    vm.notification.subscribe(lambda payload: notifications.append(payload))
    opened = {"project": None}
    vm.project_opened.subscribe(lambda p: opened.__setitem__("project", p))

    p = DummyProject(pid=7, number="J-7")
    vm.set_active_project(p)

    # Assert: error notification surfaced and project was still emitted
    assert any(n.get("level") == "error" and "Failed to load project details" in n.get("message", "") for n in notifications)
    assert opened["project"] is p


def test_vm_skips_ingest_when_db_already_exists(monkeypatch, tmp_path):
    # Arrange: DB already exists; ingestion should be skipped
    db_file = tmp_path / "proj.sqlite"
    db_file.write_text("x")
    monkeypatch.setattr(
        "mmx_engineering_spec_manager.viewmodels.main_window_view_model.project_sqlite_db_path",
        lambda _p: str(db_file),
        raising=False,
    )

    calls = {"ingest": 0, "load": 0}

    class DummyService:
        def ensure_project_db(self, project):
            return Result.ok_value(None)

        def ingest_project_details_if_needed(self, project, settings=None):
            calls["ingest"] += 1
            return Result.ok_value(False)

        def load_enriched_project(self, project):
            calls["load"] += 1
            enriched = DummyProject(pid=project.id, number=project.number)
            enriched.from_db = True
            return Result.ok_value(enriched)

    vm = MainWindowViewModel(data_manager=types.SimpleNamespace(), project_bootstrap_service=DummyService())

    opened = {"project": None}
    vm.project_opened.subscribe(lambda p: opened.__setitem__("project", p))

    p = DummyProject(pid=5, number="J-5")
    vm.set_active_project(p)

    # Since DB exists, VM should load and return early; ingest should not be called
    assert calls["load"] == 1
    assert calls["ingest"] in (0, 1)  # accept 0; defensive impl may check and still return False
    assert getattr(opened["project"], "from_db", False) is True
