"""
TrackerWidgetPanel – Petit widget d'information affiché dans Parlia

Ce composant PySide6 affiche discrètement 3 lignes de texte résumant
l’état du module Trakia (tracker) :

1. Nombre de messages actifs sur les 3 dernières heures
   ➜ ex : "17 / 80"
2. Temps avant expiration du message le plus ancien
   ➜ ex : "Expire dans 42 min"
3. Temps écoulé depuis le dernier message
   ➜ ex : "Dernier il y a 3 min"

Il est conçu pour être utilisé dans le coin supérieur droit de Parlia,
mais peut être placé ailleurs si besoin.

Fonctionnement :
- Utilise `tracker_service.getSummary()` pour récupérer les infos
- Met à jour automatiquement toutes les 60 secondes avec QTimer
- Expose une méthode publique `refresh()` pour forcer la mise à jour manuelle

Style :
- Texte blanc sur fond transparent
- Petite police lisible
- Pas de décoration inutile
"""

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from modules.trakia.services.tracker_service import get_summary


class TrackerWidgetPanel(QWidget):
    def __init__(self):
        super().__init__()

        # Configuration du style
        self.setStyleSheet(
            "background-color: transparent; color: white; font-size: 12px;"
        )

        # Layout principal
        layout = QVBoxLayout()

        # Labels pour les trois lignes de texte
        self.active_messages_label = QLabel("")
        self.expiration_label = QLabel("")
        self.last_message_label = QLabel("")

        layout.addWidget(self.active_messages_label)
        layout.addWidget(self.expiration_label)
        layout.addWidget(self.last_message_label)

        self.setLayout(layout)

        # Initialiser les données
        self.refresh()

        # Mettre à jour automatiquement toutes les 60 secondes
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(60000)

    def refresh(self):
        """Met à jour les données affichées."""
        summary = get_summary()

        self.active_messages_label.setText(f"{summary['active_count']}")
        self.expiration_label.setText(f"Expire dans {summary['expires_in']}")
        self.last_message_label.setText(f"Dernier il y a {summary['last_message']}")
