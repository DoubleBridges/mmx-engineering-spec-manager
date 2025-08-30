import os

import pytest
import requests
from unittest.mock import Mock
from mmx_engineering_spec_manager.importers.innergy_importer import InnergyImporter


def test_get_job_details_successful(mocker):
    """
    Test that the InnergyImporter can make a successful API call.
    """
    # Create a mock response object
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"job_number": "12345"}

    # Patch the requests.get method to return our mock response
    mocker.patch.object(requests, 'get', return_value=mock_response)

    # Note that the __init__ method no longer takes an API key
    importer = InnergyImporter()

    # We now pass the job_id to the method we want to test
    importer.get_job_details(job_id="12345")

    # Assert that the API call was made and the response was handled
    requests.get.assert_called_once_with(
        "https://api.innergy.com/jobs/12345",
        headers={"Authorization": f"Bearer {os.getenv('INNERGY_API_KEY')}"}
    )

def test_get_job_details_returns_data(mocker):
    """
    Test that the InnergyImporter returns the correct JSON data.
    """
    # Create a mock response with realistic job details data
    mock_job_data = {
        "job_number": "12345",
        "job_name": "New Project",
        "job_address": "123 Main St"
    }

    # Create a mock response object
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_job_data

    # Patch the requests.get method to return our mock response
    mocker.patch.object(requests, 'get', return_value=mock_response)

    # Note that the __init__ method no longer takes an API key
    importer = InnergyImporter()

    # We now pass the job_id to the method we want to test
    job_details = importer.get_job_details(job_id="12345")

    # Assert that the returned data matches our mock data
    assert job_details == mock_job_data