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