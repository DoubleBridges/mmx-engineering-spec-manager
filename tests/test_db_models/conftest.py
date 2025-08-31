import pytest
from sqlalchemy.orm import Session
from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.db_models.location import Location
from mmx_engineering_spec_manager.db_models.product import Product
from mmx_engineering_spec_manager.db_models.custom_field import CustomField
from mmx_engineering_spec_manager.db_models.prompt import Prompt
from mmx_engineering_spec_manager.db_models.specification_group import SpecificationGroup
from mmx_engineering_spec_manager.db_models.global_prompts import GlobalPrompts
from mmx_engineering_spec_manager.db_models.wizard_prompts import WizardPrompts
from mmx_engineering_spec_manager.db_models.database_config import get_engine, Base
import os


@pytest.fixture
def db_session():
    """
    Creates a new database session for each test.
    """
    # Create a temporary database file
    db_path = "test.db"
    engine = get_engine(db_path)

    # Create the tables in the database
    Base.metadata.create_all(engine)

    session = Session(bind=engine)
    yield session
    session.close()
    os.remove(db_path)