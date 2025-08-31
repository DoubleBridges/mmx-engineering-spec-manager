import pytest
from sqlalchemy.orm import Session
from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.db_models.location import Location
from mmx_engineering_spec_manager.db_models.database_config import get_engine, Base
import os


@pytest.fixture
def db_session():
    """
    Creates a new database session for each test.
    """
    # Create a temporary database file
    db_path = "test.db"
    engine = get_engine(db_path)

    # Create the tables in the database if they don't exist
    Base.metadata.create_all(engine)

    session = Session(bind=engine)
    yield session
    session.close()
    os.remove(db_path)


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