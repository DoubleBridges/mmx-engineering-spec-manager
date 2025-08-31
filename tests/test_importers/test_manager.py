import pytest
import os
import requests
from unittest.mock import Mock
from mmx_engineering_spec_manager.importers.manager import ImporterManager
from mmx_engineering_spec_manager.importers.innergy import InnergyImporter


def test_importer_manager_loads_innergy_importer(mocker):
    """
    Test that the ImporterManager can load the InnergyImporter and make a successful API call.
    """
    # Create a mock response object
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"job_number": "12345"}

    # Patch the requests.get method to return our mock response
    mocker.patch.object(requests, 'get', return_value=mock_response)

    importer_manager = ImporterManager()
    importer = importer_manager.get_importer("innergy")

    # Call the method we want to test
    importer.get_job_details(job_id="12345")

    # Assert that the API call was made and the response was handled
    requests.get.assert_called_once_with(
        "https://api.innergy.com/api/projects/12345",
        headers={"Authorization": f"Bearer {os.getenv('INNERGY_API_KEY')}"}
    )