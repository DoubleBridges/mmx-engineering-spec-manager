import pytest
from mmx_engineering_spec_manager.data_manager.manager import DataManager
from mmx_engineering_spec_manager.db_models.project import Project

def test_save_project_from_raw_data(db_session):
    """
    Test that the DataManager can save a project to the database from raw data.
    """
    raw_data = {
        "number": "101",
        "name": "Test Project",
        "job_description": "A complete project example."
    }

    data_manager = DataManager()
    data_manager.save_project(raw_data, db_session)

    retrieved_project = db_session.query(Project).filter_by(number="101").first()

    assert retrieved_project is not None
    assert retrieved_project.name == "Test Project"
    assert retrieved_project.number == "101"
    assert retrieved_project.job_description == "A complete project example."

def test_save_project_with_collections_from_raw_data(db_session):
    """
    Test that the DataManager can save a project and its collections to the database.
    """
    raw_data = {
        "number": "101",
        "name": "Test Project",
        "job_description": "A complete project example.",
        "locations": [
            {"name": "Test Location 1"},
            {"name": "Test Location 2"}
        ],
        "products": [
            {"name": "Test Product 1", "quantity": 1},
            {"name": "Test Product 2", "quantity": 2}
        ]
    }

    data_manager = DataManager()
    data_manager.save_project_with_collections(raw_data, db_session)

    retrieved_project = db_session.query(Project).filter_by(number="101").first()

    assert retrieved_project is not None
    assert len(retrieved_project.locations) == 2
    assert retrieved_project.locations[0].name == "Test Location 1"
    assert len(retrieved_project.products) == 2
    assert retrieved_project.products[0].name == "Test Product 1"

def test_save_all_collections_from_raw_data(db_session):
    """
    Test that the DataManager can save a project and all of its collections from raw data.
    """
    raw_data = {
        "number": "101",
        "name": "Test Project",
        "job_description": "A complete project example.",
        "locations": [{"name": "Test Location 1"}],
        "products": [{"name": "Test Product 1", "quantity": 1}],
        "walls": [{"link_id": "wall_1", "width": 100}],
        "custom_fields": [{"name": "Contractor", "value": "ABC Inc."}],
        "global_prompts": [{"name": "Global Prompts"}],
        "wizard_prompts": [{"name": "Wizard Prompts"}]
    }

    data_manager = DataManager()
    data_manager.save_project_with_collections(raw_data, db_session)

    retrieved_project = db_session.query(Project).filter_by(number="101").first()

    assert retrieved_project is not None
    assert len(retrieved_project.locations) == 1
    assert len(retrieved_project.products) == 1
    assert len(retrieved_project.walls) == 1
    assert retrieved_project.walls[0].link_id == "wall_1"
    assert len(retrieved_project.custom_fields) == 1
    assert retrieved_project.custom_fields[0].name == "Contractor"
    assert len(retrieved_project.global_prompts) == 1
    assert retrieved_project.global_prompts[0].name == "Global Prompts"
    assert len(retrieved_project.wizard_prompts) == 1
    assert retrieved_project.wizard_prompts[0].name == "Wizard Prompts"