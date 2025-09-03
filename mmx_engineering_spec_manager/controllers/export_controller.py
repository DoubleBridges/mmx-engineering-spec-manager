from PySide6.QtCore import QObject, Slot


class ExportController(QObject):
    """
    Controller for the Export tab.
    """
    def __init__(self, data_manager, export_tab):
        super().__init__()
        self.data_manager = data_manager
        self.export_tab = export_tab
        self._active_project = None

    @Slot(object)
    def set_active_project(self, project):
        """
        Slot to receive the currently active project.
        """
        self._active_project = project
        # We can update the view later, for now just store the project.