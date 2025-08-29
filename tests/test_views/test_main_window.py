import pytest
from PySide6.QtWidgets import QApplication
from mmx_engineering_spec_manager.views.main_window import MainWindow

@pytest.mark.skip(reason="MainWindow class not yet implemented")
def test_main_window_creation(qtbot):
    """
    Test that the main window can be created and shown without errors.
    """
    # Create an instance of the MainWindow
    window = MainWindow()
    qtbot.addWidget(window)

    # Check if the window is visible
    window.show()
    assert window.isVisible()

    # You can also check for other initial properties
    assert window.windowTitle() == "Spec Manager"