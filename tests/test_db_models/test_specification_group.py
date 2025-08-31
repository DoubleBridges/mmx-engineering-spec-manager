import pytest
from mmx_engineering_spec_manager.db_models.specification_group import SpecificationGroup

def test_specification_group_model_creation(db_session):
    """
    Test that the SpecificationGroup model can be created with basic properties.
    """
    spec_group = SpecificationGroup(
        name="Test Spec Group"
    )
    db_session.add(spec_group)
    db_session.commit()

    retrieved_spec_group = db_session.query(SpecificationGroup).filter_by(name="Test Spec Group").first()

    assert retrieved_spec_group.name == "Test Spec Group"