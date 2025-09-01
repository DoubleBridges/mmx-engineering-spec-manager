from mmx_engineering_spec_manager.db_models.project import Project
from mmx_engineering_spec_manager.db_models.location import Location
from mmx_engineering_spec_manager.db_models.product import Product
from mmx_engineering_spec_manager.db_models.custom_field import CustomField


class DataIngester:
    def __init__(self):
        self.project = None

    def ingest_project_data(self, importer, job_id, session):
        project_payload = importer.get_job_details(job_id)

        project = Project(
            number=project_payload.get("Number"),
            name=project_payload.get("Name"),
            job_description=project_payload.get("JobDescription"),
            job_address=project_payload.get("Address", {}).get("Address1", "")
        )

        session.add(project)

        locations_payload = importer.get_job_locations(job_id)

        self.load_locations(project, locations_payload, session)

        products_payload = importer.get_products(job_id)

        self.load_products(project, products_payload, session)

        session.commit()

        self.project = project

    def load_locations(self, project, locations_payload, session):
        for location_data in locations_payload.get("locations", []):
            location = Location(
                name=location_data.get("name"),
                project=project
            )
            session.add(location)

    def load_products(self, project, products_payload, session):
        for product_data in products_payload.get("Items", []):
            product = Product(
                name=product_data.get("Name"),
                quantity=product_data.get("QuantCount"),
                project=project
            )
            session.add(product)

            custom_fields_payload = product_data.get("CustomFields", [])
            self.load_custom_fields(product, custom_fields_payload, session)

    def load_custom_fields(self, product, custom_fields_payload, session):
        for cf_data in custom_fields_payload:
            custom_field = CustomField(
                name=cf_data.get("Name"),
                value=cf_data.get("Value"),
                product=product
            )
            session.add(custom_field)