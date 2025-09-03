from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mmx_engineering_spec_manager.db_models.appliance_callout import \
    ApplianceCallout
from mmx_engineering_spec_manager.db_models.custom_field import CustomField
from mmx_engineering_spec_manager.db_models.database_config import Base
from mmx_engineering_spec_manager.db_models.finish_callout import FinishCallout
from mmx_engineering_spec_manager.db_models.global_prompts import GlobalPrompts
from mmx_engineering_spec_manager.db_models.hardware_callout import \
    HardwareCallout
from mmx_engineering_spec_manager.db_models.location import Location
from mmx_engineering_spec_manager.db_models.product import Product
from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.db_models.prompt import Prompt
from mmx_engineering_spec_manager.db_models.sink_callout import SinkCallout
from mmx_engineering_spec_manager.db_models.specification_group import \
    SpecificationGroup
from mmx_engineering_spec_manager.db_models.wall import Wall
from mmx_engineering_spec_manager.db_models.wizard_prompts import WizardPrompts


class DataManager:
    def __init__(self):
        engine = create_engine("sqlite:///projects.db")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
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