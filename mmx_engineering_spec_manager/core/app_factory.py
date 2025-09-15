from __future__ import annotations


def build_main_window():
    """UI-aware factory for constructing the application's MainWindow.

    This keeps composition_root UI-free while providing a single entry point
    for the app to construct the primary window with all transitional wiring
    already handled inside the view itself.

    Additionally, instantiate the legacy MainWindowController to ensure the
    Projects tab is populated at startup and the Innergy import action is
    wired. This is a transitional adapter during MVVM migration.
    """
    from mmx_engineering_spec_manager.views.main_window import MainWindow  # local import to avoid UI import in composition_root
    from mmx_engineering_spec_manager.data_manager.manager import DataManager
    from mmx_engineering_spec_manager.controllers.main_window_controller import MainWindowController

    # Construct the main window
    main_window = MainWindow()

    # Instantiate DataManager and legacy controller to wire Projects and Import actions
    try:
        dm = DataManager()
        # Make DataManager available to MainWindow for legacy product load/save handlers
        # (transitional: _on_load_products_from_innergy and _on_save_products_changes)
        try:
            setattr(main_window, "_data_manager", dm)
        except Exception:
            pass
        # Pass the ViewModel if present to bridge events
        vm = getattr(main_window, "_vm", None)
        MainWindowController(main_window=main_window, data_manager=dm, view_model=vm)
    except Exception:
        # If controller wiring fails (e.g., in headless tests), proceed with window only
        pass

    return main_window
