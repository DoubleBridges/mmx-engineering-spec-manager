import types

from mmx_engineering_spec_manager.viewmodels import AttributesViewModel
from mmx_engineering_spec_manager.services import Result


class DummyProject:
    def __init__(self, pid):
        self.id = pid


def test_save_callouts_uses_service_and_emits_success_notification():
    # Arrange
    records = []

    class DummyService:
        def save_callouts(self, project_id, rows_or_grouped):
            records.append((project_id, rows_or_grouped))
            return Result.ok_value(None)

    vm = AttributesViewModel(data_manager=None, attributes_service=DummyService())
    vm.set_active_project(DummyProject(10))

    notifications = []
    vm.notification.subscribe(lambda p: notifications.append(p))

    rows = [
        {"Type": "Finishes", "Name": "Matte", "Tag": "MAT-01", "Description": "Matte Finish"},
        {"Type": "Hardware", "Name": "Hinge", "Tag": "H-01", "Description": "Soft close"},
    ]

    # Act
    ok = vm.save_callouts_for_active_project(rows)

    # Assert
    assert ok is True
    assert records == [(10, rows)]
    assert any(n.get("level") == "info" and "Callouts saved" in n.get("message", "") for n in notifications)


def test_save_callouts_service_failure_emits_error_and_returns_false():
    # Arrange
    class DummyService:
        def save_callouts(self, project_id, rows_or_grouped):
            return Result.fail("boom")

    vm = AttributesViewModel(data_manager=None, attributes_service=DummyService())
    vm.set_active_project(DummyProject(11))

    notifications = []
    vm.notification.subscribe(lambda p: notifications.append(p))

    rows = [
        {"Type": "Finishes", "Name": "Matte", "Tag": "MAT-01", "Description": "Matte Finish"},
    ]

    # Act
    ok = vm.save_callouts_for_active_project(rows)

    # Assert
    assert ok is False
    assert any(n.get("level") == "error" and "boom" in n.get("message", "") for n in notifications)
