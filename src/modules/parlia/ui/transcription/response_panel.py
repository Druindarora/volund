# response_panel.py

from typing import Optional

import qtawesome as qta
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QLabel, QTextEdit, QToolButton, QVBoxLayout, QWidget


class ResponsePanel(QWidget):
    """Zone de texte réponse (IA/API)."""

    copyResponseRequested = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Ligne en haut : Label + bouton copier aligné à droite
        row = QHBoxLayout()
        label = QLabel("Réponse", self)
        label.setStyleSheet("font-weight: bold;")
        row.addWidget(label)

        row.addStretch()  # espace flexible pour pousser le bouton à droite

        self.copyResponseButton = QToolButton(self)
        self.copyResponseButton.setToolTip("Copier la réponse")
        self.copyResponseButton.setIcon(qta.icon("fa5s.copy", color="#B0E0E6"))
        self.copyResponseButton.clicked.connect(self._emitCopyResponse)
        row.addWidget(self.copyResponseButton)

        layout.addLayout(row)

        # Zone de texte
        self.textEdit = QTextEdit(self)
        self.textEdit.setPlaceholderText("Réponse IA")
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

    def _emitCopyResponse(self) -> None:
        self.copyResponseRequested.emit()
