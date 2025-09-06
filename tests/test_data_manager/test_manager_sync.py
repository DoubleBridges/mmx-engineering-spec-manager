import pytest
from mmx_engineering_spec_manager.data_manager.manager import DataManager


def test_sync_projects_from_innergy_calls_create_and_commit(db_session, mocker):
    dm = DataManager()

    # Mock the importer to return a project payload
    mocked_importer_cls = mocker.patch(
        'mmx_engineering_spec_manager.data_manager.manager.InnergyImporter'
    )
    mocked_importer_instance = mocked_importer_cls.return_value
    mocked_importer_instance.get_projects.return_value = [
        {"Number": "200", "Name": "From Innergy", "Address": "123 Road"}
    ]

    # Spy on create_or_update_project to ensure it is called with formatted data
    mocker.patch.object(dm, 'create_or_update_project')

    # Spy on session.commit passed into the method
    mock_commit = mocker.patch.object(db_session, 'commit')

    dm.sync_projects_from_innergy(db_session)

    dm.create_or_update_project.assert_called_once_with(
        {"number": "200", "name": "From Innergy", "job_description": "123 Road"},
        db_session
    )
    assert mock_commit.call_count == 1
