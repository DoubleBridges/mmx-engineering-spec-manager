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
        # Run lightweight SQLite migration to add any missing product columns (safe no-op otherwise)
        try:
            from mmx_engineering_spec_manager.utilities.migrations import (
                migrate_sqlite_products_add_missing_columns,
                migrate_sqlite_walls_add_missing_columns,
                migrate_sqlite_global_prompts_add_missing_columns,
                migrate_sqlite_wizard_prompts_add_missing_columns,
            )
            migrate_sqlite_products_add_missing_columns(engine)
            migrate_sqlite_walls_add_missing_columns(engine)
            migrate_sqlite_global_prompts_add_missing_columns(engine)
            migrate_sqlite_wizard_prompts_add_missing_columns(engine)
        except Exception:  # pragma: no cover
            pass
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

    def sync_projects_from_innergy(self, session=None, progress=None):
        """
        Imports projects from Innergy API and saves them to the database.
        Raises RuntimeError on configuration or HTTP errors; callers should handle and surface to UI.
        Returns:
            int: number of imported/updated projects
        """
        logger = get_logger(__name__)
        db_session = session if session is not None else self.session
        settings = get_settings()
        if progress:
            try:
                progress(5)
            except Exception:
                pass
        if not settings.innergy_base_url or not settings.innergy_api_key:
            logger.warning(
                "Innergy API key or base URL missing; proceeding (tests may mock importer). UI should validate settings before invoking sync."
            )
        importer = InnergyImporter()
        logger.info("Starting Innergy projects sync from %s", settings.innergy_base_url)
        try:
            projects_data = importer.get_projects()
            imported = 0
            total = len(projects_data) if projects_data else 0
            if progress:
                try:
                    progress(10)
                except Exception:
                    pass
            if projects_data:
                for idx, project_data in enumerate(projects_data, start=1):
                    # Adapt the Innergy data to the format expected by our database models
                    # Normalize address and description safely (avoid dicts in text fields)
                    addr = project_data.get("Address")
                    if isinstance(addr, dict):
                        address_str = addr.get("Address1") or addr.get("address1") or addr.get("Address") or ""  # pragma: no cover
                    else:
                        address_str = str(addr or "")
                    # Prefer explicit JobDescription; fall back to address string for backward-compat and to avoid dicts
                    job_desc = project_data.get("JobDescription") or address_str
                    # Keep formatted_data minimal to satisfy existing expectations/tests
                    formatted_data = {
                        "number": project_data.get("Number"),
                        "name": project_data.get("Name"),
                        "job_description": job_desc,
                    }
                    self.create_or_update_project(formatted_data, db_session)
                    imported += 1
                    if progress and total > 0:
                        try:
                            base = 10
                            span = 85
                            pct = base + int(span * (idx / total))
                            progress(min(99, pct))
                        except Exception:
                            pass
                db_session.commit()
            if progress:
                try:
                    progress(100)
                except Exception:
                    pass
            logger.info("Innergy projects sync finished. Imported/updated: %d", imported)
            return imported
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
            if hasattr(project, "job_address"):
                project.job_address = raw_data.get("job_address")
        else:
            project = Project(
                number=raw_data.get("number"),
                name=raw_data.get("name"),
                job_description=raw_data.get("job_description"),
                job_address=raw_data.get("job_address")
            )
            db_session.add(project)
        db_session.commit()
        return project

    def replace_callouts_for_project(self, project_id: int, grouped: dict, session=None):
        """
        Replace all callouts for a project with the provided grouped callouts.
        `grouped` is a dict with keys: "Finishes", "Hardware", "Sinks", "Appliances", "Uncategorized".
        Values are lists of DTOs having attributes: name/material, tag, description.
        Uncategorized items are ignored unless assigned a concrete type by the UI before saving.
        """
        db_session = session if session is not None else self.session
        # Clear existing
        db_session.query(FinishCallout).filter_by(project_id=project_id).delete(synchronize_session=False)
        db_session.query(HardwareCallout).filter_by(project_id=project_id).delete(synchronize_session=False)
        db_session.query(SinkCallout).filter_by(project_id=project_id).delete(synchronize_session=False)
        db_session.query(ApplianceCallout).filter_by(project_id=project_id).delete(synchronize_session=False)

        # Helper to add
        def add_many(model_cls, items):
            for d in items or []:
                # Support either DTOs or dicts
                name = getattr(d, 'name', None) or (d.get('name') if isinstance(d, dict) else None) or getattr(d, 'Name', None) or (d.get('Name') if isinstance(d, dict) else None)
                tag = getattr(d, 'tag', None) or (d.get('tag') if isinstance(d, dict) else None) or getattr(d, 'Tag', None) or (d.get('Tag') if isinstance(d, dict) else None)
                desc = getattr(d, 'description', None) or (d.get('description') if isinstance(d, dict) else None) or getattr(d, 'Description', None) or (d.get('Description') if isinstance(d, dict) else None)
                if not name or not tag:
                    continue
                obj = model_cls(project_id=project_id)
                # Map to CalloutMixin fields (material, tag, description)
                setattr(obj, 'material', str(name))
                setattr(obj, 'tag', str(tag))
                setattr(obj, 'description', str(desc) if desc is not None else None)
                db_session.add(obj)

        add_many(FinishCallout, grouped.get("Finishes"))
        add_many(HardwareCallout, grouped.get("Hardware"))
        add_many(SinkCallout, grouped.get("Sinks"))
        add_many(ApplianceCallout, grouped.get("Appliances"))
        # Uncategorized are not persisted until categorized
        db_session.commit()