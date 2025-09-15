import types

from mmx_engineering_spec_manager.viewmodels import MainWindowViewModel
from mmx_engineering_spec_manager.services import Result


class DummyProject:
    def __init__(self, pid):
        self.id = pid


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