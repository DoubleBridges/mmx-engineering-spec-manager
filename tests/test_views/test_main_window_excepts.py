import types
from PySide6.QtWidgets import QTabWidget

from mmx_engineering_spec_manager.views.main_window import MainWindow


def test_main_window_exception_branches(qtbot, monkeypatch):
    mw = MainWindow()
    qtbot.addWidget(mw)

    # Monkeypatch tab_widget.setTabEnabled to raise to cover try/except in _set_non_project_tabs_enabled
    def raising_setTabEnabled(idx, enabled):
        raise RuntimeError("boom")
    monkeypatch.setattr(mw.tab_widget, "setTabEnabled", raising_setTabEnabled)

    # Call private to hit except path
    mw._set_non_project_tabs_enabled(True)

    # Monkeypatch projects_tab.display_project_details to raise to cover try/except
    def raise_display(project):
        raise RuntimeError("boom2")
    monkeypatch.setattr(mw.projects_tab, "display_project_details", raise_display)

    # Monkeypatch signal emit to raise to cover try/except in set_current_project
    def raise_emit(project):
        raise RuntimeError("boom3")
    monkeypatch.setattr(mw, "current_project_changed", types.SimpleNamespace(emit=raise_emit))

    class Dummy:
        pass

    mw._on_project_loaded(Dummy())
