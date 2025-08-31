import pytest
from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.db_models.specification_group import SpecificationGroup
from mmx_engineering_spec_manager.db_models.finish_callout import FinishCallout

def test_finish_callout_model_creation(db_session):
    """
    Test that the FinishCallout model can be created and linked to a Project and SpecificationGroup.
    """
    project = Project(
        number="101",
        name="Test Project",
        job_description="A complete project example."
    )
    db_session.add(project)
    db_session.commit()

    spec_group = SpecificationGroup(
        name="Test Spec Group"
    )
    db_session.add(spec_group)
    db_session.commit()

    finish_callout = FinishCallout(
        material="PLAM",
        tag="PL1",
        description="NEVAMAR VA 7002 COOL CHIC",
        project_id=project.id,
        specification_group_id=spec_group.id
    )
    db_session.add(finish_callout)
    db_session.commit()

    retrieved_callout = db_session.query(FinishCallout).filter_by(tag="PL1").first()

    assert retrieved_callout.material == "PLAM"
    assert retrieved_callout.tag == "PL1"
    assert retrieved_callout.description == "NEVAMAR VA 7002 COOL CHIC"
    assert retrieved_callout.project_id == project.id
    assert retrieved_callout.specification_group_id == spec_group.id