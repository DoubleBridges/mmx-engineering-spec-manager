import pytest
from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.db_models.specification_group import SpecificationGroup
from mmx_engineering_spec_manager.db_models.hardware_callout import HardwareCallout

def test_hardware_callout_model_creation(db_session):
    """
    Test that the HardwareCallout model can be created and linked to a Project and SpecificationGroup.
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

    hardware_callout = HardwareCallout(
        material="PULL",
        tag="CP1",
        description="MOCKETT D254A 94",
        project_id=project.id,
        specification_group_id=spec_group.id
    )
    db_session.add(hardware_callout)
    db_session.commit()

    retrieved_callout = db_session.query(HardwareCallout).filter_by(tag="CP1").first()

    assert retrieved_callout.material == "PULL"
    assert retrieved_callout.tag == "CP1"
    assert retrieved_callout.description == "MOCKETT D254A 94"
    assert retrieved_callout.project_id == project.id
    assert retrieved_callout.specification_group_id == spec_group.id