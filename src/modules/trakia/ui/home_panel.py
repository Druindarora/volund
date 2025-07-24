from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from ..settings import LABELS

class HomePanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel(f"{LABELS['home_title']} : Trakia")
        layout.addWidget(label)
        self.setLayout(layout)
