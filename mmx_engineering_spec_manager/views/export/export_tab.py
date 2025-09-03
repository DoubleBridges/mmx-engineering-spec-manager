from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class ExportTab(QWidget):
    """
    The main widget for the 'Export' tab.
    """
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel("Export controls will go here."))
