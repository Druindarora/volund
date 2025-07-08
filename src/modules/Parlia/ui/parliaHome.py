from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from modules.parlia import ModuleInfo


class ParliaHome(QWidget):
    def __init__(self, main_window: QMainWindow):
        super().__init__(main_window)
        self.main_window = main_window
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        layout.addWidget(self._create_title())
        layout.addWidget(self._create_separator())
        layout.addWidget(self._create_settings_block())

        layout.addStretch()
        self.setLayout(layout)

    def _create_title(self) -> QLabel:
        title = QLabel(f"Bienvenue dans {ModuleInfo.name}")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title.setContentsMargins(0, 0, 0, 20)
        return title

    def _create_separator(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #666666; background-color: #666666; height: 1px;")
        return line

    def _create_settings_block(self) -> QWidget:
        # Bloc placeholder pour les futurs paramètres (ex: choix du modèle Whisper)
        container = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        label = QLabel("⚙️ Paramètres Whisper (à venir)")
        label.setFont(QFont("Arial", 14, QFont.Weight.Normal))
        layout.addWidget(label)

        container.setLayout(layout)
        return container
