import pytest
from mmx_engineering_spec_manager.db_models.project import Project

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