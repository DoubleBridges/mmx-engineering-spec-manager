import types

from mmx_engineering_spec_manager.viewmodels import WorkspaceViewModel
from mmx_engineering_spec_manager.services import Result


class DummyProject:
    def __init__(self, pid):
        self.id = pid


def test_load_uses_service_and_updates_state():
    # Arrange a dummy service that returns a simple tree
    calls = {"load": []}

    class DummyService:
        def load_project_tree(self, project_id):
            calls["load"].append(project_id)
            return {"project": {"id": project_id, "locations": []}}

        def save_changes(self, changes):
            return Result.ok_value(None)

    vm = WorkspaceViewModel(workspace_service=DummyService())
    vm.set_active_project(DummyProject(99))

    events = {"tree": None}
    vm.tree_loaded.subscribe(lambda t: events.__setitem__("tree", t))

    # Act
    tree = vm.load()

    # Assert
    assert calls["load"] == [99]
    assert isinstance(tree, dict) and tree.get("project", {}).get("id") == 99
    assert vm.view_state.tree == tree
    assert events["tree"] == tree
    assert vm.view_state.is_loading is False
    assert vm.view_state.error is None


def test_save_changes_success_clears_dirty_and_emits_notification():
    notes = []

    class DummyService:
        def load_project_tree(self, project_id):
            return {"project": {"id": project_id}}

        def save_changes(self, changes):
            return Result.ok_value(None)

    vm = WorkspaceViewModel(workspace_service=DummyService())
    vm.set_active_project(DummyProject(7))
    vm.mark_dirty(True)
    vm.notification.subscribe(lambda p: notes.append(p))

    ok = vm.save_changes({"some": "change"})

    assert ok is True
    assert vm.view_state.dirty is False
    assert any(n.get("level") == "info" for n in notes)


def test_load_or_save_failure_sets_error_and_returns_false(monkeypatch):
    class FailingService:
        def load_project_tree(self, project_id):
            raise RuntimeError("load failed")

        def save_changes(self, changes):
            return Result.fail("boom")

    vm = WorkspaceViewModel(workspace_service=FailingService())
    vm.set_active_project(DummyProject(3))

    # load failure
    tree = vm.load()
    assert tree == {}
    assert vm.view_state.error and "load failed" in vm.view_state.error

    # save failure
    ok = vm.save_changes({})
    assert ok is False
    assert vm.view_state.error and "boom" in vm.view_state.error
