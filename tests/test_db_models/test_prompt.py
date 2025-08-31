import pytest
from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.db_models.location import Location
from mmx_engineering_spec_manager.db_models.product import Product
from mmx_engineering_spec_manager.db_models.prompt import Prompt

def test_prompt_model_creation(db_session):
    """
    Test that the Prompt model can be created with basic properties.
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

    product = Product(
        name="Test Product",
        quantity=1,
        width=18,
        height=34.5,
        depth=23.125,
        project_id=project.id,
        location_id=location.id
    )
    db_session.add(product)
    db_session.commit()

    prompt = Prompt(
        name="Door_Type",
        value="MV Profile Door",
        product_id=product.id
    )
    db_session.add(prompt)
    db_session.commit()

    assert prompt.name == "Door_Type"
    assert prompt.value == "MV Profile Door"
    assert prompt.product_id == product.id