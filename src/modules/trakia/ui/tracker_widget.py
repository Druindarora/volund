from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from modules.trakia.services.tracker_service import get_summary


class TrackerWidgetPanel(QWidget):
    def __init__(self):
        super().__init__()

        # Style CRT rétro vert phosphorescent
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(10, 31, 10, 180);
                color: #90ff90;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                border-radius: 10px;
                padding: 8px;
            }
            QLabel {
                padding: 2px 4px;
            }

        """)

        # Layout vertical
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        # Trois lignes
        self.active_messages_label = QLabel("")
        self.expiration_label = QLabel("")
        self.last_message_label = QLabel("")

        layout.addWidget(self.active_messages_label)
        layout.addWidget(self.expiration_label)
        layout.addWidget(self.last_message_label)

        self.setLayout(layout)

        # Données + timer auto
        self.refresh()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(60000)

    def refresh(self):
        summary = get_summary()
        self.active_messages_label.setText(f"Trakia : {summary['active_count']}")
        self.expiration_label.setText(f"Expire dans {summary['expires_in']}")
        self.last_message_label.setText(f"Dernier il y a {summary['last_message']}")
