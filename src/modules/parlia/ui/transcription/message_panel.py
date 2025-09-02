# message_panel.py

from typing import Optional

import qtawesome as qta
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from modules.parlia.i18n.parlia_strings import ParliaStrings


class MessagePanel(QWidget):
    """Zone de texte transcrit (utilisateur)."""

    copyMessageRequested = Signal()
    clearRequested = Signal()  # notification optionnelle au parent

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Ligne en haut : Label + boutons alignés à droite
        row = QHBoxLayout()
        label = QLabel(ParliaStrings.Transcription.TRANSCRIBED_TEXT, self)
        label.setStyleSheet("font-weight: bold;")
        row.addWidget(label)

        row.addStretch()  # espace flexible au milieu

        self.copyMessageButton = QToolButton(self)
        self.copyMessageButton.setToolTip("Copier le message")
        self.copyMessageButton.setIcon(qta.icon("fa5s.copy", color="#E5E5E5"))
        self.copyMessageButton.clicked.connect(self._emitCopyMessage)
        row.addWidget(self.copyMessageButton)

        self.clearButton = QToolButton(self)
        self.clearButton.setObjectName("clearButton")
        self.clearButton.setToolTip("Effacer la transcription")
        self.clearButton.setIcon(qta.icon("fa5s.trash", color="#d9534f"))
        self.clearButton.clicked.connect(self.clearMessageContent)
        row.addWidget(self.clearButton)

        layout.addLayout(row)

        # Zone de texte
        self.textEdit = QTextEdit(self)
        self.textEdit.setObjectName("messageTextEdit")  # ⬅️ NEW: objectName pour ciblage QSS
        self.textEdit.setPlaceholderText(ParliaStrings.Transcription.TRANSCRIBED_TEXT)
        self.textEdit.setAcceptRichText(True)
        self.textEdit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.textEdit.setFont(QFont("Courier New", 10))
        self.textEdit.setStyleSheet("padding: 10px;")
        self.textEdit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.textEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        layout.addWidget(self.textEdit)

    def setText(self, text: str) -> None:
        self.textEdit.setPlainText(text)

    def getText(self) -> str:
        return self.textEdit.toPlainText()

    def clear(self) -> None:
        self.textEdit.clear()

    def clearMessageContent(self) -> None:
        """Efface uniquement le contenu du MessagePanel et notifie éventuellement le parent."""
        self.setText("")
        self.clearRequested.emit()

    def setLimitExceeded(self, exceeded: bool) -> None:
        """Active/désactive le style 'limite dépassée' (bordure rouge discrète)."""
        if exceeded:
            self.textEdit.setStyleSheet(
                "border: 1px solid #d9534f; border-radius: 4px; padding: 10px;"
            )
        else:
            self.textEdit.setStyleSheet("padding: 10px;")

    def _emitCopyMessage(self) -> None:
        self.copyMessageRequested.emit()
