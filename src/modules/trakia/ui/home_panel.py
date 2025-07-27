from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QTabWidget, QVBoxLayout, QWidget

from modules.trakia.settings import LABELS
from modules.trakia.ui.messages_panel import MessagesPanel
from modules.trakia.ui.statistics_panel import StatisticsPanel


class HomePanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Titre centré avec une taille de police augmentée
        title_label = QLabel(f"{LABELS['home_title']} : Trakia")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)

        # Système d'onglets
        tab_widget = QTabWidget()

        # Onglet Statistiques
        statistics_panel = StatisticsPanel()
        tab_widget.addTab(statistics_panel, "Statistiques")

        # Onglet Messages
        messages_panel = MessagesPanel()
        tab_widget.addTab(messages_panel, "Messages")

        layout.addWidget(tab_widget)
        self.setLayout(layout)
