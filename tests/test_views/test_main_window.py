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


def test_main_window_has_file_menu(main_window):
    """
    Test that the main window has a 'File' menu.
    """
    # Check if the main window has a menu bar
    menu_bar = main_window.menuBar()
    assert menu_bar is not None

    # Check for the 'File' menu by name
    file_menu = None
    for action in menu_bar.actions():
        if action.text() == "&File":
            file_menu = action.menu()
            break

    assert file_menu is not None
    assert file_menu.title() == "&File"