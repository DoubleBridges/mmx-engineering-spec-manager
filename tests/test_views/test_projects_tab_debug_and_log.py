import os
import pytest
from PySide6.QtWidgets import QPlainTextEdit

from mmx_engineering_spec_manager.views.projects.projects_tab import ProjectsTab


def test_projects_tab_uses_log_view_in_debug_mode(qtbot, monkeypatch):
    monkeypatch.setenv("DEBUG_SHOW_INNERGY_RESPONSE", "1")
    tab = ProjectsTab()
    qtbot.addWidget(tab)

    # Ensure log_view exists and is a QPlainTextEdit
    assert isinstance(tab.log_view, QPlainTextEdit)

    # Normal display_log_text path (try branch)
    tab.display_log_text("hello")
    assert tab.log_view.toPlainText() == "hello"

    # Force exception branch by making setPlainText raise
    def bad_set(text):
        raise RuntimeError("boom")
    monkeypatch.setattr(tab.log_view, 'setPlainText', bad_set)

    # Should not raise due to except path
    tab.display_log_text("ignored")
