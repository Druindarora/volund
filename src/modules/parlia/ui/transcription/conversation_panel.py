# conversation_panel.py

from typing import Optional

from PySide6.QtWidgets import (
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.modules.parlia.ui.transcription.message_panel import MessagePanel
from src.modules.parlia.ui.transcription.response_panel import ResponsePanel


class ConversationPanel(QWidget):
    """Partie droite : onglets Message/Response, orchestrés par le TranscriptionPanel."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        root = QVBoxLayout(self)

        self.tabs = QTabWidget(self)

        self.messagePanel = MessagePanel(self)
        self.responsePanel = ResponsePanel(self)

        self.tabs.addTab(self.messagePanel, "Message")
        self.tabs.addTab(self.responsePanel, "Réponse")

        root.addWidget(self.tabs)

    # --- API attendue ---

    def setMessageText(self, text: str) -> None:
        self.messagePanel.setText(text)

    def setResponseText(self, text: str) -> None:
        self.responsePanel.setText(text)

    def getMessageText(self) -> str:
        return self.messagePanel.getText()

    def getResponseText(self) -> str:
        return self.responsePanel.getText()

    def clear(self) -> None:
        # Réinitialise les deux onglets
        self.messagePanel.setText("")
        self.responsePanel.setText("")
