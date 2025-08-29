from PySide6.QtWidgets import QMainWindow, QMenu, QMenuBar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spec Manager")

        # Create the menu bar
        self.menu_bar = self.menuBar()

        # Add the 'File' menu
        self.file_menu = self.menu_bar.addMenu("&File")