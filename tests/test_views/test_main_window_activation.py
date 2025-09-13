from PySide6.QtWidgets import QTabWidget

from mmx_engineering_spec_manager.views.main_window import MainWindow


class DummyProj:
    def __init__(self, number, name, job_description=""):
        self.number = number
        self.name = name
        self.job_description = job_description


def test_tabs_activation_on_project_load(qtbot):
    mw = MainWindow()
    qtbot.addWidget(mw)

    tab_widget: QTabWidget = mw.findChild(QTabWidget)

    # Tabs should be disabled initially (except Projects)
    assert not tab_widget.isTabEnabled(mw._idx_attributes)
    assert not tab_widget.isTabEnabled(mw._idx_workspace)
    assert not tab_widget.isTabEnabled(mw._idx_export)

    dummy = DummyProj("P-1", "Alpha")

    # Emit signal as ProjectsTab would
    mw.projects_tab.open_project_signal.emit(dummy)

    # Now enabled and current_project set
    assert tab_widget.isTabEnabled(mw._idx_attributes)
    assert tab_widget.isTabEnabled(mw._idx_workspace)
    assert tab_widget.isTabEnabled(mw._idx_export)
    assert mw.current_project is dummy
