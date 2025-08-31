import pytest
from sqlalchemy.orm import Session
from mmx_engineering_spec_manager.db_models.project import Project
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

def test_project_model_creation(db_session):
    """
    Test that the Project model can be created with basic properties.
    """
    project = Project(
        number="101",
        name="Test Project",
        job_description="A complete project example."
    )
    db_session.add(project)
    db_session.commit()

    retrieved_project = db_session.query(Project).filter_by(number="101").first()

    assert retrieved_project.number == "101"
    assert retrieved_project.name == "Test Project"
    assert retrieved_project.job_description == "A complete project example."