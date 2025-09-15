import sys

from PySide6.QtWidgets import QApplication

from mmx_engineering_spec_manager.views.main_window import MainWindow


def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)

    # Set application metadata for QSettings, QStandardPaths, etc.
    app.setOrganizationName("MMX")
    app.setApplicationName("Engineering Spec Manager")

    # Initialize the main window (VMs are wired via composition_root inside the view)
    main_window = MainWindow()

    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()