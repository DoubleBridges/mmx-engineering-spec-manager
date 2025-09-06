import pytest
from mmx_engineering_spec_manager.data_manager.manager import DataManager
from mmx_engineering_spec_manager.importers.innergy import InnergyImporter


def test_sync_projects_from_innergy_raises_on_exception(mocker):
    dm = DataManager()
    # Patch get_projects to raise to drive exception path
    mocker.patch.object(InnergyImporter, 'get_projects', side_effect=RuntimeError('boom'))

    with pytest.raises(Exception):
        dm.sync_projects_from_innergy()
