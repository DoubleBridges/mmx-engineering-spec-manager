import pytest
from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.db_models.global_prompts import GlobalPrompts

def test_global_prompts_creation(db_session):
    """
    Test that the GlobalPrompts model can be created with a relationship to a Project.
    """
    project = Project(
        number="101",
        name="Test Project",
        job_description="A complete project example."
    )
    db_session.add(project)
    db_session.commit()

    global_prompts = GlobalPrompts(
        name="Test Global Prompts",
        project_id=project.id
    )
    db_session.add(global_prompts)
    db_session.commit()

    assert global_prompts.name == "Test Global Prompts"
    assert global_prompts.project_id == project.id
    assert global_prompts.project.name == "Test Project"