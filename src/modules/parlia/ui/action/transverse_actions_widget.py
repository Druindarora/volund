# transverse_actions_widget.py
from __future__ import annotations

from typing import Optional

import qtawesome as qta
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget


class TransverseActionsWidget(QWidget):
    """UI for Transverse Actions tab: two visual buttons (no logic)."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        layout.addWidget(self.createCopyAndFocusButton())
        layout.addWidget(self.createSendToOllamaButton())

        layout.addStretch()
        self.setLayout(layout)

    def createCopyAndFocusButton(self) -> QPushButton:
        btn = QPushButton("Copy & Focus", self)
        btn.setObjectName("copyAndFocusButton")
        btn.setIcon(qta.icon("fa5s.clipboard", color="#222222"))
        btn.setIconSize(QSize(18, 18))
        btn.setMinimumHeight(36)
        btn.setStyleSheet(
            "background-color: #4A90E2; color: black; border-radius: 8px; padding: 8px;"
        )
        return btn

    def createSendToOllamaButton(self) -> QPushButton:
        btn = QPushButton("Send to Ollama", self)
        btn.setObjectName("sendToOllamaButton")
        btn.setIcon(qta.icon("fa5s.paper-plane", color="#222222"))
        btn.setIconSize(QSize(18, 18))
        btn.setMinimumHeight(36)
        btn.setStyleSheet(
            "background-color: #50C878; color: black; border-radius: 8px; padding: 8px;"
        )
        return btn
