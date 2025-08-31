import pytest
from PySide6.QtWidgets import QMenu
from PySide6.QtWidgets import QTabWidget, QWidget

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


def test_exit_action_closes_window(main_window, qtbot):
    """
    Test that the Exit action on the File menu closes the main window.
    """
    # Find the 'Exit' action
    file_menu = main_window.findChild(QMenu, "file_menu")
    assert file_menu is not None

    exit_action = None
    for action in file_menu.actions():
        if action.text() == "E&xit":
            exit_action = action
            break

    assert exit_action is not None

    # Trigger the action and wait for the main window's 'close' signal
    with qtbot.waitSignal(main_window.close_event_signal, timeout=500):
        exit_action.trigger()

    # The test will pass if the signal is received within the timeout

def test_main_window_has_projects_tab(main_window):
    """
    Test that the main window contains a QTabWidget with a 'Projects' tab.
    """
    # Find the QTabWidget
    tab_widget = main_window.findChild(QTabWidget)
    assert tab_widget is not None

    # Check that the 'Projects' tab exists
    projects_tab = None
    for i in range(tab_widget.count()):
        if tab_widget.tabText(i) == "Projects":
            projects_tab = tab_widget.widget(i)
            break

    assert projects_tab is not None
    assert isinstance(projects_tab, QWidget)