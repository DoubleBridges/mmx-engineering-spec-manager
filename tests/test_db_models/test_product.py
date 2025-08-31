import pytest
from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.db_models.location import Location
from mmx_engineering_spec_manager.db_models.product import Product
from mmx_engineering_spec_manager.db_models.wall import Wall


def test_product_model_creation(db_session):
    """
    Test that the Product model can be created with basic properties.
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

    wall = Wall(
        link_id="BPWALL.Wall.001",
        link_id_location="Phase One",
        width=120,
        height=108.0,
        depth=6.0,
        project_id=project.id,
        location_id=location.id
    )
    db_session.add(wall)
    db_session.commit()

    product = Product(
        name="Test Product",
        quantity=1,
        width=18,
        height=34.5,
        depth=23.125,
        project_id=project.id,
        location_id=location.id,
        wall_id=wall.id
    )
    db_session.add(product)
    db_session.commit()

    assert product.name == "Test Product"
    assert product.quantity == 1
    assert product.width == 18
    assert product.height == 34.5
    assert product.depth == 23.125
    assert product.project_id == project.id
    assert product.location_id == location.id
    assert product.wall_id == wall.id