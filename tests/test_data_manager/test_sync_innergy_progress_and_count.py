import types
from mmx_engineering_spec_manager.data_manager.manager import DataManager
from mmx_engineering_spec_manager.importers.innergy import InnergyImporter


def test_sync_projects_reports_progress_and_returns_count(monkeypatch):
    dm = DataManager()

    # Valid settings to avoid early return warning path
    monkeypatch.setattr(
        'mmx_engineering_spec_manager.data_manager.manager.get_settings',
        lambda: types.SimpleNamespace(innergy_base_url="https://app.innergy.com", innergy_api_key="KEY")
    )

    # Provide three mock projects
    projects = [
        {"Number": f"P-{i}", "Name": f"Proj{i}", "Address": "Addr"}
        for i in range(3)
    ]
    monkeypatch.setattr(InnergyImporter, 'get_projects', lambda self: projects)

    # Avoid DB work inside create_or_update_project to speed up
    monkeypatch.setattr(dm, 'create_or_update_project', lambda *a, **k: None)

    values = []
    def progress_cb(v):
        values.append(int(v))

    count = dm.sync_projects_from_innergy(progress=progress_cb)

    # Should report initial and mid progress as well as loop and completion
    assert 5 in values
    assert 10 in values
    assert any(11 <= v <= 99 for v in values), f"expected at least one loop progress value <=99, got: {values}"
    assert 100 in values

    assert count == len(projects)
