import pytest
import requests
from unittest.mock import Mock
from mmx_engineering_spec_manager.importers.innergy_importer import InnergyImporter


def test_get_job_details_successful():
    """
    Test that the InnergyImporter can make a successful API call.
    """
    # Create an instance of the InnergyImporter
    importer = InnergyImporter("test_api_key")

    # Create a mock response object
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"job_number": "12345"}

    # Patch the requests.get method to return our mock response
    requests.get = Mock(return_value=mock_response)

    # Call the method we want to test
    importer.get_job_details()

    # Assert that the API call was made and the response was handled
    requests.get.assert_called_once_with(
        "https://api.innergy.com/jobs/12345",
        headers={"Authorization": "Bearer test_api_key"}
    )