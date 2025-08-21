# message_panel.py

from typing import Optional

import qtawesome as qta
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QLabel, QTextEdit, QToolButton, QVBoxLayout, QWidget

from modules.parlia.i18n.parlia_strings import ParliaStrings


class MessagePanel(QWidget):
    """Zone de texte transcrit (utilisateur)."""

    copyMessageRequested = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Ligne en haut : Label + bouton copier aligné à droite
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

        layout.addLayout(row)

        # Zone de texte
        self.textEdit = QTextEdit(self)
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

    def _emitCopyMessage(self) -> None:
        self.copyMessageRequested.emit()
