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

        messages = get_all_messages()
        cutoff_time = datetime.now() - timedelta(hours=3)
        recent_messages = [
            msg
            for msg in messages
            if "timestamp" in msg
            and msg["timestamp"]
            and datetime.fromisoformat(msg["timestamp"]) > cutoff_time
        ]

        # Trier par date décroissante
        recent_messages.sort(
            key=lambda msg: datetime.fromisoformat(msg["timestamp"]), reverse=True
        )

        for msg in recent_messages:
            try:
                dt = datetime.fromisoformat(msg["timestamp"])
                hour_str = dt.strftime("%H:%M")
            except Exception:
                hour_str = "??:??"
            content = msg.get("text", "")
            content_preview = (content[:60] + "...") if len(content) > 60 else content
            item = QListWidgetItem(f"[{hour_str}] {content_preview}")
            item.setToolTip(content)
            self.message_list.addItem(item)
