import pytest
from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.db_models.specification_group import SpecificationGroup
from mmx_engineering_spec_manager.db_models.appliance_callout import ApplianceCallout

def test_appliance_callout_model_creation(db_session):
    """
    Test that the ApplianceCallout model can be created and linked to a Project and SpecificationGroup.
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

    appliance_callout = ApplianceCallout(
        material="MICROWAVE",
        tag="AP1",
        description="TBD, ARCH/GC PLEASE SPECIFY, 19",
        project_id=project.id,
        specification_group_id=spec_group.id
    )
    db_session.add(appliance_callout)
    db_session.commit()

    retrieved_callout = db_session.query(ApplianceCallout).filter_by(tag="AP1").first()

    assert retrieved_callout.material == "MICROWAVE"
    assert retrieved_callout.tag == "AP1"
    assert retrieved_callout.description == "TBD, ARCH/GC PLEASE SPECIFY, 19"
    assert retrieved_callout.project_id == project.id
    assert retrieved_callout.specification_group_id == spec_group.id