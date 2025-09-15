import sys

from PySide6.QtWidgets import QApplication

from mmx_engineering_spec_manager.core.app_factory import build_main_window


def main():
    """Main function to run the application."""
    app = QApplication(sys.argv)

    # Set application metadata for QSettings, QStandardPaths, etc.
    app.setOrganizationName("MMX")
    app.setApplicationName("Engineering Spec Manager")

    # Initialize the main window via the app factory (keeps composition_root UI-free)
    main_window = build_main_window()

    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()