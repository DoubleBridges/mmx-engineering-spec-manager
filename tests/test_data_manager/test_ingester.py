import pytest
from unittest.mock import Mock
from mmx_engineering_spec_manager.data_manager.ingester import DataIngester
from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.db_models.location import Location
from mmx_engineering_spec_manager.db_models.product import Product
from mmx_engineering_spec_manager.db_models.custom_field import CustomField


def test_ingester_ingests_project_data(db_session, mocker):
    """
    Test that the DataIngester can ingest a complete project payload.
    """
    mock_project_payload = {
        "Id": "123-abc",
        "Number": "101",
        "Name": "Test Project",
        "Address": {"Address1": "123 Main St", "City": "Anytown", "State": "CA"}
    }

    mock_locations_payload = {
        "locations": [
            {"id": "loc1", "name": "Kitchen"}
        ]
    }

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

    mock_importer = Mock()
    mock_importer.get_job_details.return_value = mock_project_payload
    mock_importer.get_job_locations.return_value = mock_locations_payload
    mock_importer.get_products.return_value = mock_products_payload

    ingester = DataIngester()

    ingester.ingest_project_data(importer=mock_importer, job_id="12345", session=db_session)

    assert ingester.project is not None
    assert ingester.project.number == "101"
    assert ingester.project.name == "Test Project"
    assert ingester.project.job_address == "123 Main St"

    assert len(ingester.project.locations) == 1
    assert ingester.project.locations[0].name == "Kitchen"

    assert len(ingester.project.products) == 1
    assert ingester.project.products[0].name == "1 Door Base"
    assert ingester.project.products[0].quantity == 1

    assert len(ingester.project.products[0].custom_fields) == 1
    assert ingester.project.products[0].custom_fields[0].name == "Door_Type"