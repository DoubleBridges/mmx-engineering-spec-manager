import pytest
from mmx_engineering_spec_manager.models.microvellum_model import ProjectModel
from mmx_engineering_spec_manager.models.location_model import LocationModel

def test_project_model_creation():
    """
    Test that the ProjectModel can be created with basic properties.
    """
    # Create an instance of the ProjectModel
    project_data = {
        "Name": "Test Project",
        "JobNumber": "98765"
    }
    project = ProjectModel(project_data)

    # Assert that the properties were set correctly
    assert project.name == "Test Project"
    assert project.job_number == "98765"
    assert project.category is None

def test_project_model_all_properties():
    """
    Test that all ProjectModel properties can be set and are accessible.
    """
    project_data = {
        "Name": "Full Project Test",
        "JobDescription": "A complete project example.",
        "JobNumber": "MV123",
        "Category": "Estimates",
        "JobAddress": "123 Main St.",
        "JobPhone": "555-123-4567",
        "JobFax": "555-987-6543",
        "JobEmail": "test@example.com"
    }

    project = ProjectModel(project_data)

    assert project.name == "Full Project Test"
    assert project.job_description == "A complete project example."
    assert project.job_number == "MV123"
    assert project.category == "Estimates"
    assert project.job_address == "123 Main St."
    assert project.job_phone == "555-123-4567"
    assert project.job_fax == "555-987-6543"
    assert project.job_email == "test@example.com"

def test_project_model_empty_collections():
    """
    Test that the ProjectModel can be created with empty collections.
    """
    project_data = {}
    project = ProjectModel(project_data)

    assert project.locations == []
    assert project.walls == []
    assert project.products == []

def test_project_model_with_locations():
    """
    Test that the ProjectModel can be created with a list of LocationModels.
    """
    project_data = {
        "Locations": [
            {"Name": "Kitchen"},
            {"Name": "Bathroom"}
        ]
    }
    project = ProjectModel(project_data)

    assert len(project.locations) == 2
    assert isinstance(project.locations[0], LocationModel)
    assert project.locations[0].name == "Kitchen"
    assert project.locations[1].name == "Bathroom"