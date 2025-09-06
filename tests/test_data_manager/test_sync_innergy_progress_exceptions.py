import types
from mmx_engineering_spec_manager.data_manager.manager import DataManager
from mmx_engineering_spec_manager.importers.innergy import InnergyImporter


def test_sync_projects_progress_callbacks_exceptions(monkeypatch):
    dm = DataManager()
    # Valid settings
    monkeypatch.setattr(
        'mmx_engineering_spec_manager.data_manager.manager.get_settings',
        lambda: types.SimpleNamespace(innergy_base_url='http://x', innergy_api_key='k')
    )
    # One project to iterate
    monkeypatch.setattr(InnergyImporter, 'get_projects', lambda self: [{"Number":"P-1","Name":"N","Address":"A"}])
    # No-op for DB
    monkeypatch.setattr(dm, 'create_or_update_project', lambda *a, **k: None)

    def bad_progress(v):
        raise RuntimeError('boom')

    # Should not raise despite progress exceptions
    count = dm.sync_projects_from_innergy(progress=bad_progress)
    assert count == 1
