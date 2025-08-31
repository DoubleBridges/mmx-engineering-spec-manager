from mmx_engineering_spec_manager.importers.innergy import InnergyImporter

class ImporterManager:
    def __init__(self):
        pass

    def get_importer(self, importer_name):
        if importer_name == "innergy":
            return InnergyImporter()
        return None