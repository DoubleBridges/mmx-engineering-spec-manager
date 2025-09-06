from mmx_engineering_spec_manager.importers.innergy import InnergyImporter
from mmx_engineering_spec_manager.importers.project_setup_wizard import ProjectSetupWizardImporter
from mmx_engineering_spec_manager.importers.registry import get_importer as get_registered_importer


class ImporterManager:
    def __init__(self):
        pass

    def get_importer(self, importer_name):
        # Preserve legacy behavior for built-in names to keep tests and API stable
        if importer_name == "innergy":
            return InnergyImporter()
        if importer_name == "project_setup_wizard":
            return ProjectSetupWizardImporter()
        # Otherwise, consult the plugin registry
        return get_registered_importer(importer_name)