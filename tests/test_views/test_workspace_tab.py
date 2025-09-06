import pytest
from PySide6.QtWidgets import QTabWidget, QWidget
from mmx_engineering_spec_manager.views.main_window import MainWindow
from mmx_engineering_spec_manager.views.workspace.workspace_tab import WorkspaceTab

def test_main_window_has_workspace_tab(qtbot):
    """
    Test that the main window contains a QTabWidget with a 'Workspace' tab.
    """
    main_window = MainWindow()
    qtbot.addWidget(main_window)

    # Find the QTabWidget
    tab_widget = main_window.findChild(QTabWidget)
    assert tab_widget is not None

    # Check that the 'Workspace' tab exists
    workspace_tab = None
    for i in range(tab_widget.count()):
        if tab_widget.tabText(i) == "Workspace":
            workspace_tab = tab_widget.widget(i)
            break

    assert workspace_tab is not None
    assert isinstance(workspace_tab, WorkspaceTab)


def test_workspace_tab_display_project_data_updates_label(qtbot):
    from mmx_engineering_spec_manager.views.workspace.workspace_tab import WorkspaceTab

    class P:
        def __init__(self):
            self.name = "ProjName"
            self.number = "PN-1"

    tab = WorkspaceTab()
    qtbot.addWidget(tab)
    tab.display_project_data(P())
    assert tab.current_project is not None
    assert "ProjName (PN-1)" in tab.project_label.text()
