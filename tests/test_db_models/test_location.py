import pytest
from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.db_models.location import Location

def test_location_model_creation(db_session):
    """
    Test that the Location model can be created with basic properties.
    """
    project = Project(
        number="101",
        name="Test Project",
        job_description="A complete project example."
    )
    db_session.add(project)
    db_session.commit()

    location = Location(
        name="Test Location",
        project_id=project.id
    )
    db_session.add(location)
    db_session.commit()

    assert location.name == "Test Location"
    assert location.project_id == project.id