import os
from pathlib import Path

from PySide6.QtCore import QStandardPaths
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mmx_engineering_spec_manager.db_models.appliance_callout import \
    ApplianceCallout
from mmx_engineering_spec_manager.db_models.custom_field import CustomField
from mmx_engineering_spec_manager.db_models.database_config import Base
from mmx_engineering_spec_manager.db_models.finish_callout import FinishCallout
from mmx_engineering_spec_manager.db_models.global_prompts import GlobalPrompts
from mmx_engineering_spec_manager.db_models.hardware_callout import HardwareCallout
from mmx_engineering_spec_manager.db_models.location import Location
from mmx_engineering_spec_manager.db_models.product import Product
from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.db_models.prompt import Prompt
from mmx_engineering_spec_manager.db_models.sink_callout import SinkCallout
from mmx_engineering_spec_manager.db_models.specification_group import SpecificationGroup
from mmx_engineering_spec_manager.db_models.wall import Wall
from mmx_engineering_spec_manager.db_models.wizard_prompts import WizardPrompts
from mmx_engineering_spec_manager.importers.innergy import InnergyImporter
from mmx_engineering_spec_manager.utilities.persistence import create_engine_and_sessionmaker
from mmx_engineering_spec_manager.utilities.settings import get_settings
from mmx_engineering_spec_manager.utilities.logging_config import get_logger


class DataManager:
    def __init__(self):
        # Initialize DB engine/session using centralized persistence config (supports SQLite/Postgres)
        engine, Session = create_engine_and_sessionmaker()
        # Ensure schema exists
        Base.metadata.create_all(engine)
        self.session = Session()

    def save_project(self, raw_data, session=None):
        self.create_or_update_project(raw_data, session)

    def save_project_with_collections(self, raw_data, session=None):
        db_session = session if session is not None else self.session
        project = Project(
            number=raw_data.get("number"),
            name=raw_data.get("name"),
            job_description=raw_data.get("job_description")
        )

        # Add locations to the project
        if "locations" in raw_data:
            for location_data in raw_data["locations"]:
                location = Location(
                    name=location_data.get("name"),
                    project=project
                )
                project.locations.append(location)

        # Add products to the project
        if "products" in raw_data:
            for product_data in raw_data["products"]:
                product = Product(
                    name=product_data.get("name"),
                    quantity=product_data.get("quantity"),
                    project=project
                )
                project.products.append(product)

        # Add walls to the project
        if "walls" in raw_data:
            for wall_data in raw_data["walls"]:
                wall = Wall(
                    link_id=wall_data.get("link_id"),
                    width=wall_data.get("width"),
                    project=project
                )
                project.walls.append(wall)

        # Add custom fields to the project
        if "custom_fields" in raw_data:
            for cf_data in raw_data["custom_fields"]:
                custom_field = CustomField(
                    name=cf_data.get("name"),
                    value=cf_data.get("value"),
                    project=project
                )
                project.custom_fields.append(custom_field)

        # Add global prompts to the project
        if "global_prompts" in raw_data:
            for gp_data in raw_data["global_prompts"]:
                global_prompts = GlobalPrompts(
                    name=gp_data.get("name"),
                    project=project
                )
                project.global_prompts.append(global_prompts)

        # Add wizard prompts to the project
        if "wizard_prompts" in raw_data:
            for wp_data in raw_data["wizard_prompts"]:
                wizard_prompts = WizardPrompts(
                    name=wp_data.get("name"),
                    project=project
                )
                project.wizard_prompts.append(wizard_prompts)

        db_session.add(project)
        db_session.commit()

    def get_all_projects(self, session=None):
        db_session = session if session is not None else self.session
        return db_session.query(Project).all()

    def sync_projects_from_innergy(self, session=None):
        """
        Imports projects from Innergy API and saves them to the database.
        Raises RuntimeError on configuration or HTTP errors; callers should handle and surface to UI.
        """
        logger = get_logger(__name__)
        db_session = session if session is not None else self.session
        settings = get_settings()
        if not settings.innergy_base_url or not settings.innergy_api_key:
            logger.warning(
                "Innergy API key or base URL missing; proceeding (tests may mock importer). UI should validate settings before invoking sync."
            )
        importer = InnergyImporter()
        logger.info("Starting Innergy projects sync from %s", settings.innergy_base_url)
        try:
            projects_data = importer.get_projects()
            imported = 0
            if projects_data:
                for project_data in projects_data:
                    # Adapt the Innergy data to the format expected by our database models
                    formatted_data = {
                        "number": project_data.get("Number"),
                        "name": project_data.get("Name"),
                        "job_description": project_data.get("Address", "")
                    }
                    self.create_or_update_project(formatted_data, db_session)
                    imported += 1
                db_session.commit()
            logger.info("Innergy projects sync finished. Imported/updated: %d", imported)
        except Exception as e:
            logger.exception("Innergy projects sync failed: %s", e)
            raise

    def get_project_by_id(self, project_id, session=None):
        db_session = session if session is not None else self.session
        return db_session.query(Project).get(project_id)

    def create_or_update_project(self, raw_data, session=None):
        db_session = session if session is not None else self.session
        project = db_session.query(Project).filter_by(number=raw_data.get("number")).first()
        if project:
            project.name = raw_data.get("name")
            project.job_description = raw_data.get("job_description")
        else:
            project = Project(
                number=raw_data.get("number"),
                name=raw_data.get("name"),
                job_description=raw_data.get("job_description")
            )
            db_session.add(project)
        db_session.commit()
        return project