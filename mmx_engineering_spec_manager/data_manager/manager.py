from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.db_models.location import Location
from mmx_engineering_spec_manager.db_models.product import Product
from mmx_engineering_spec_manager.db_models.wall import Wall
from mmx_engineering_spec_manager.db_models.custom_field import CustomField
from mmx_engineering_spec_manager.db_models.global_prompts import GlobalPrompts
from mmx_engineering_spec_manager.db_models.wizard_prompts import WizardPrompts


class DataManager:
    def __init__(self):
        pass

    def save_project(self, raw_data, session):
        project = Project(
            number=raw_data.get("number"),
            name=raw_data.get("name"),
            job_description=raw_data.get("job_description")
        )
        session.add(project)
        session.commit()

    def save_project_with_collections(self, raw_data, session):
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

        session.add(project)
        session.commit()

    def get_all_projects(self, session):
        return session.query(Project).all()