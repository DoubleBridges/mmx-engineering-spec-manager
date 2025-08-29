import pytest
from mmx_engineering_spec_manager.views.main_window import MainWindow

@pytest.fixture
def main_window(qtbot):
    """
    Fixture to create and manage the MainWindow instance for each test.
    """
    window = MainWindow()
    qtbot.addWidget(window)
    return window

def test_main_window_creation(main_window):
    """
    Test that the main window can be created and shown without errors.
    """
    # Check if the window is visible
    main_window.show()
    assert main_window.isVisible()

    # Check for other initial properties
    assert main_window.windowTitle() == "Spec Manager"