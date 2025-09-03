import sys

from PySide6.QtWidgets import QApplication

from mmx_engineering_spec_manager.controllers.main_window_controller import MainWindowController
from mmx_engineering_spec_manager.data_manager.manager import DataManager
from mmx_engineering_spec_manager.views.main_window import MainWindow


def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)

    # Set application metadata for QSettings, QStandardPaths, etc.
    app.setOrganizationName("MMX")
    app.setApplicationName("Engineering Spec Manager")

    # Initialize the database and data manager
    data_manager = DataManager()

    # Initialize the main window and controller
    main_window = MainWindow()
    main_controller = MainWindowController(
        main_window=main_window,
        data_manager=data_manager
    )

    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()