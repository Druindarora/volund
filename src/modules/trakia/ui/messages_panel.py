from datetime import datetime, timedelta

from PySide6.QtWidgets import QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from modules.trakia.services.tracker_service import get_all_messages


class MessagesPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # Liste des messages
        self.message_list = QListWidget()
        self.populate_messages()

        layout.addWidget(self.message_list)
        self.setLayout(layout)

    def populate_messages(self):
        self.message_list.clear()  # nettoyage de la liste existante

        # Récupération des messages depuis le service
        messages = get_all_messages()

        # Filtrer les messages des 3 dernières heures
        cutoff_time = datetime.now() - timedelta(hours=3)
        recent_messages = [
            msg
            for msg in messages
            if datetime.fromisoformat(msg["timestamp"]) > cutoff_time
        ]

        # Trier par ordre décroissant
        recent_messages.sort(
            key=lambda msg: datetime.fromisoformat(msg["timestamp"]), reverse=True
        )

        for msg in recent_messages:
            time_str = msg["hour_str"]
            content = msg["text"]
            content_preview = (content[:60] + "...") if len(content) > 60 else content
            item = QListWidgetItem(f"[{time_str}] {content_preview}")
            item.setToolTip(content)
            self.message_list.addItem(item)
