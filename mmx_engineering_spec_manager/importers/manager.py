from mmx_engineering_spec_manager.importers.innergy import InnergyImporter
from mmx_engineering_spec_manager.importers.project_setup_wizard import ProjectSetupWizardImporter


class ImporterManager:
    def __init__(self):
        pass

    def get_importer(self, importer_name):
        if importer_name == "innergy":
            return InnergyImporter()
        if importer_name == "project_setup_wizard":
            return ProjectSetupWizardImporter()
        return None