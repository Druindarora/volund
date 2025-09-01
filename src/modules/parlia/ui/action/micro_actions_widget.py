# micro_actions_widget.py
from __future__ import annotations

from typing import Optional

import qtawesome as qta
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MicroActionsWidget(QWidget):
    """UI for Micro Actions tab: 3 sections with visual buttons only (no logic)."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        mainLayout = QVBoxLayout(self)
        mainLayout.setSpacing(12)
        mainLayout.setContentsMargins(8, 8, 8, 8)

        # --- Section 1: Code Understanding ---
        mainLayout.addWidget(self._sectionHeader("Code Understanding"))
        understandingRow = QHBoxLayout()
        understandingRow.setSpacing(8)
        understandingRow.addWidget(
            self._makeButton(
                text="Explain Code",
                iconName="fa5s.question-circle",
                colorHex="#4A90E2",
                objectName="explainCodeButton",
            )
        )
        understandingRow.addWidget(
            self._makeButton(
                text="Summarize File",
                iconName="fa5s.file-alt",
                colorHex="#50C878",
                objectName="summarizeFileButton",
            )
        )
        understandingRow.addWidget(
            self._makeButton(
                text="Add Documentation",
                iconName="fa5s.book",
                colorHex="#FFD700",
                objectName="addDocumentationButton",
            )
        )
        understandingRow.addStretch()
        mainLayout.addLayout(understandingRow)

        # --- Section 2: Code Quality ---
        mainLayout.addWidget(self._sectionHeader("Code Quality"))
        qualityRow = QHBoxLayout()
        qualityRow.setSpacing(8)
        qualityRow.addWidget(
            self._makeButton(
                text="Analyze Code",
                iconName="fa5s.search",
                colorHex="#FFA500",
                objectName="analyzeCodeButton",
            )
        )
        qualityRow.addWidget(
            self._makeButton(
                text="Refactor Code",
                iconName="fa5s.magic",
                colorHex="#40E0D0",
                objectName="refactorCodeButton",
            )
        )
        qualityRow.addWidget(
            self._makeButton(
                text="Format Code",
                iconName="fa5s.align-left",
                colorHex="#9370DB",
                objectName="formatCodeButton",
            )
        )
        qualityRow.addWidget(
            self._makeButton(
                text="Suggest Improvements",
                iconName="fa5s.lightbulb",
                colorHex="#FF8C00",
                objectName="suggestImprovementsButton",
            )
        )
        qualityRow.addStretch()
        mainLayout.addLayout(qualityRow)

        # --- Section 3: Tests ---
        mainLayout.addWidget(self._sectionHeader("Tests"))
        testsRow = QHBoxLayout()
        testsRow.setSpacing(8)
        testsRow.addWidget(
            self._makeButton(
                text="Generate Tests",
                iconName="fa5s.vial",
                colorHex="#20B2AA",
                objectName="generateTestsButton",
            )
        )
        testsRow.addWidget(
            self._makeButton(
                text="Regenerate Tests",
                iconName="fa5s.redo",
                colorHex="#FF6347",
                objectName="regenerateTestsButton",
            )
        )
        testsRow.addStretch()
        mainLayout.addLayout(testsRow)

        mainLayout.addStretch()
        self.setLayout(mainLayout)

    def _sectionHeader(self, text: str) -> QLabel:
        lbl = QLabel(text, self)
        lbl.setStyleSheet("font-weight: bold; color: #E5E5E5; margin-top: 6px;")
        return lbl

    def _makeButton(
        self, *, text: str, iconName: str, colorHex: str, objectName: str
    ) -> QPushButton:
        btn = QPushButton(text, self)
        btn.setObjectName(objectName)
        btn.setIcon(qta.icon(iconName, color="#222222"))
        btn.setIconSize(QSize(18, 18))
        btn.setMinimumHeight(36)
        btn.setStyleSheet(
            f"background-color: {colorHex}; color: black; border-radius: 8px; padding: 8px;"
        )
        return btn
