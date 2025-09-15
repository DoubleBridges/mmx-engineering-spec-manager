import types

from mmx_engineering_spec_manager.viewmodels import MainWindowViewModel


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