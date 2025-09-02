import pytest

from mmx_engineering_spec_manager.db_models.custom_field import CustomField
from mmx_engineering_spec_manager.db_models.project import Project

@pytest.fixture
def project():
    return Project(
        number="101",
        name="Test Project",
        job_description="A complete project example."
    )

def test_project_model_creation(db_session, project):
    """
    Test that the Project model can be created with basic properties.
    """
    db_session.add(project)
    db_session.commit()

    retrieved_project = db_session.query(Project).filter_by(number="101").first()

    assert retrieved_project.number == "101"
    assert retrieved_project.name == "Test Project"
    assert retrieved_project.job_description == "A complete project example."

def test_project_has_custom_fields(db_session, project):
    """
    Test that a project can have a custom field.
    """
    db_session.add(project)
    db_session.commit()

    custom_field = CustomField(
        name="Contractor",
        value="ABC Inc.",
        project_id=project.id
    )
    db_session.add(custom_field)
    db_session.commit()

    assert len(project.custom_fields) == 1
    assert project.custom_fields[0].name == "Contractor"
    assert project.custom_fields[0].value == "ABC Inc."