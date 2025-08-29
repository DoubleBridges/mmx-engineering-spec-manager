from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QMenu, QMenuBar
from PySide6.QtCore import QCoreApplication, Signal


class MainWindow(QMainWindow):
    close_event_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spec Manager")

        # Create the menu bar
        self.menu_bar = self.menuBar()

        # Add the 'File' menu
        self.file_menu = self.menu_bar.addMenu("&File")
        self.file_menu.setObjectName("file_menu")  # Set the object name for the test

        # Add the 'Exit' action to the 'File' menu
        self.exit_action = QAction("E&xit", self)
        self.file_menu.addAction(self.exit_action)

        # Connect the 'Exit' action to the close method
        self.exit_action.triggered.connect(self.close)

    def closeEvent(self, event):
        """
        Overrides the close event to emit a custom signal.
        """
        self.close_event_signal.emit()
        event.accept()
        super().closeEvent(event)