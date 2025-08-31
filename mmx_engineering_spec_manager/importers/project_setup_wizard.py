class ProjectSetupWizardImporter:
    def get_project_data(self, form_data):
        return {
            "job_number": form_data.get("job_number"),
            "name": form_data.get("name"),
            "job_description": form_data.get("job_description")
        }