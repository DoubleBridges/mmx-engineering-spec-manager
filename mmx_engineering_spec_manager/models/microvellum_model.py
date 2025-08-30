from mmx_engineering_spec_manager.models.location_model import LocationModel
from mmx_engineering_spec_manager.models.wall_model import WallModel
from mmx_engineering_spec_manager.models.product_model import ProductModel
from mmx_engineering_spec_manager.models.specification_group_model import SpecificationGroupModel


class ProjectModel:
    def __init__(self, data):
        self.name = data.get("Name")
        self.job_number = data.get("JobNumber")
        self.category = data.get("Category")
        self.job_description = data.get("JobDescription")
        self.job_address = data.get("JobAddress")
        self.job_phone = data.get("JobPhone")
        self.job_fax = data.get("JobFax")
        self.job_email = data.get("JobEmail")

        # Initialize collections
        self.locations = []
        self.walls = []
        self.products = []
        self.specification_groups = []

        if "Locations" in data:
            for location_data in data["Locations"]:
                self.locations.append(LocationModel(location_data))

        if "Walls" in data:
            for wall_data in data["Walls"]:
                self.walls.append(WallModel(wall_data))

        if "Products" in data:
            for product_data in data["Products"]:
                self.products.append(ProductModel(product_data))

        if "SpecificationGroups" in data:
            for spec_group_data in data["SpecificationGroups"]:
                self.specification_groups.append(SpecificationGroupModel(spec_group_data))