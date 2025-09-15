from __future__ import annotations


def build_main_window():
    """UI-aware factory for constructing the application's MainWindow.

    This keeps composition_root UI-free while providing a single entry point
    for the app to construct the primary window with all MVVM wiring handled
    inside the view itself via the composition_root builders.

    Legacy controllers are fully retired; no controller adapters are created here.
    """
    from mmx_engineering_spec_manager.views.main_window import MainWindow  # local import to avoid UI import in composition_root

    # Construct the main window (it wires ViewModels internally via composition_root)
    main_window = MainWindow()

    # No controllers or legacy DataManager injection.
    return main_window
