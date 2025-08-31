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
        "https://api.innergy.com/api/projects/12345",
        headers={"Authorization": f"Bearer {os.getenv('INNERGY_API_KEY')}"}
    )

def test_get_job_details_returns_data(mocker):
    """
    Test that the InnergyImporter returns the correct JSON data for a single job.
    """
    # Create a mock response with realistic job details data
    mock_job_data = {
        "Id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "Number": "12345",
        "Name": "New Project",
        "Address": {
            "Address1": "123 Main St",
            "Address2": "string",
            "City": "Anytown",
            "State": "CA",
            "ZipCode": "90210",
            "Country": "string",
            "County": "string"
        }
    }

    # Create a mock response object
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_job_data

    # Patch the requests.get method to return our mock response
    mocker.patch.object(requests, 'get', return_value=mock_response)

    importer = InnergyImporter()

    # Call the method and get the returned data
    job_details = importer.get_job_details(job_id="12345")

    # Assert that the returned data is a dictionary
    assert isinstance(job_details, dict)

    # Assert that the returned data matches our mock data
    assert job_details["Id"] == "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    assert job_details["Number"] == "12345"
    assert job_details["Name"] == "New Project"
    assert job_details["Address"]["Address1"] == "123 Main St"

    # Assert that the correct API call was made
    requests.get.assert_called_once_with(
        "https://api.innergy.com/api/projects/12345",
        headers={"Authorization": f"Bearer {os.getenv('INNERGY_API_KEY')}"}
    )


def test_get_projects_returns_filtered_data(mocker):
    """
    Test that the InnergyImporter returns a clean, filtered list of project data.
    """
    # Mock a full Innergy projects payload
    mock_projects_payload = {
        "Items": [
            {
                "Id": "123-abc",
                "Number": "101",
                "Name": "Project One",
                "Customer": {"Name": "Customer A"},
                "Address": {"Address1": "123 Main St", "City": "Anytown", "State": "CA"},
                "Status": "Active"
            },
            {
                "Id": "456-def",
                "Number": "102",
                "Name": "Project Two",
                "Customer": {"Name": "Customer B"},
                "Address": {"Address1": "456 Oak Ave", "City": "Sometwon", "State": "NY"},
                "Status": "Archived"
            }
        ]
    }

    # Define the expected filtered data
    expected_data = [
        {
            "Id": "123-abc",
            "Number": "101",
            "Name": "Project One",
            "Address": {"Address1": "123 Main St", "City": "Anytown", "State": "CA"}
        },
        {
            "Id": "456-def",
            "Number": "102",
            "Name": "Project Two",
            "Address": {"Address1": "456 Oak Ave", "City": "Sometwon", "State": "NY"}
        }
    ]

    # Create a mock response object
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_projects_payload

    # Patch the requests.get method to return our mock response
    mocker.patch.object(requests, 'get', return_value=mock_response)

    importer = InnergyImporter()

    # Call the new method we are about to build
    projects_data = importer.get_projects()

    # Assert that the returned data is a filtered list
    assert projects_data == expected_data

    # Assert that the correct API call was made
    requests.get.assert_called_once_with(
        "https://api.innergy.com/api/projects",
        headers={"Authorization": f"Bearer {os.getenv('INNERGY_API_KEY')}"}
    )

def test_get_products_with_custom_fields_returns_data(mocker):
    """
    Test that the InnergyImporter returns a clean list of products with custom fields.
    """
    # Mock a full Innergy products payload
    mock_products_payload = {
        "Items": [
            {
                "Name": "1 Door Base",
                "QuantCount": 1,
                "Description": "Test Product",
                "CustomFields": [
                    {
                        "Name": "Door_Type",
                        "Type": 0,
                        "Value": "MV Profile Door"
                    }
                ]
            }
        ]
    }

    # Define the expected filtered data
    expected_data = [
        {
            "Name": "1 Door Base",
            "QuantCount": 1,
            "Description": "Test Product",
            "CustomFields": [
                {
                    "Name": "Door_Type",
                    "Value": "MV Profile Door"
                }
            ]
        }
    ]

    # Create a mock response object
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = mock_products_payload

    # Patch the requests.get method to return our mock response
    mocker.patch.object(requests, 'get', return_value=mock_response)

    importer = InnergyImporter()

    # Call the new method we are about to build
    products_data = importer.get_products(job_id="12345")

    # Assert that the returned data is a filtered list
    assert products_data == expected_data