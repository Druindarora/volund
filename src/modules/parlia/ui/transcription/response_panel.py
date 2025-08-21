# response_panel.py

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QTextEdit, QVBoxLayout, QWidget


class ResponsePanel(QWidget):
    """Zone de texte réponse (IA/API)."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)

        label = QLabel("Réponse", self)
        label.setStyleSheet("font-weight: bold;")
        layout.addWidget(label)

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
