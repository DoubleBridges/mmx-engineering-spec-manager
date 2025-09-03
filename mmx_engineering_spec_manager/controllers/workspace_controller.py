from PySide6.QtCore import QObject, Slot


class WorkspaceController(QObject):
    """
    Controller for the Workspace tab.
    """
    def __init__(self, data_manager, workspace_tab):
        super().__init__()
        self.data_manager = data_manager
        self.workspace_tab = workspace_tab

    @Slot(object)
    def set_active_project(self, project):
        """
        Slot to receive the currently active project and update the view.
        """
        self.workspace_tab.display_project_data(project)
