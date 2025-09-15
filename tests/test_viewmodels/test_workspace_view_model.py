from mmx_engineering_spec_manager.viewmodels import WorkspaceViewModel


class DummyProject:
    def __init__(self, pid):
        self.id = pid


def test_set_active_project_updates_state():
    vm = WorkspaceViewModel()
    p = DummyProject(pid=42)
    vm.set_active_project(p)
    assert vm.view_state.active_project_id == 42
