from __future__ import annotations


def build_main_window():
    """UI-aware factory for constructing the application's MainWindow.

    This keeps composition_root UI-free while providing a single entry point
    for the app to construct the primary window with all transitional wiring
    already handled inside the view itself.
    """
    from mmx_engineering_spec_manager.views.main_window import MainWindow  # local import to avoid UI import in composition_root

    return MainWindow()
