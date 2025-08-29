from mmx_engineering_spec_manager.models.location_model import LocationModel

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

        if "Locations" in data:
            for location_data in data["Locations"]:
                self.locations.append(LocationModel(location_data))