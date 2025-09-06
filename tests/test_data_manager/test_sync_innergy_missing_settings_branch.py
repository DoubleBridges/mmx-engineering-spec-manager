import types
from mmx_engineering_spec_manager.data_manager.manager import DataManager
from mmx_engineering_spec_manager.importers.innergy import InnergyImporter


def test_sync_projects_missing_settings_warns_and_returns_zero(monkeypatch):
    dm = DataManager()
    # Missing settings (empty URL and key)
    monkeypatch.setattr(
        'mmx_engineering_spec_manager.data_manager.manager.get_settings',
        lambda: types.SimpleNamespace(innergy_base_url='', innergy_api_key=None)
    )
    # get_projects returns empty list to follow through
    monkeypatch.setattr(InnergyImporter, 'get_projects', lambda self: [])

    count = dm.sync_projects_from_innergy()
    assert count == 0
