import pytest
from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.db_models.location import Location
from mmx_engineering_spec_manager.db_models.wall import Wall

def test_wall_model_creation(db_session):
    """
    Test that the Wall model can be created with a relationship to a Project and Location.
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

    assert wall.link_id == "BPWALL.Wall.001"
    assert wall.width == 120
    assert wall.project_id == project.id
    assert wall.location_id == location.id

    assert wall.project.name == "Test Project"
    assert wall.location.name == "Test Location"