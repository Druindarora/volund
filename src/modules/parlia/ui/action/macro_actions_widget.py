# macro_actions_widget.py
from __future__ import annotations

from typing import Optional

import qtawesome as qta
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QDialog, QGridLayout, QPushButton, QWidget

from src.modules.parlia.ui.dialogs.create_module_dialog import CreateModuleDialog


class MacroActionsWidget(QWidget):
    """UI for Macro Actions tab: 6 buttons in a 2x3 grid (visual only)."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        grid = QGridLayout(self)
        grid.setSpacing(10)
        grid.setContentsMargins(8, 8, 8, 8)

        # Row 0
        grid.addWidget(self.createCreateNewModuleButton(), 0, 0)
        grid.addWidget(self.createGenerateFromSpecButton(), 0, 1)
        grid.addWidget(self.createRunTestsGlobalButton(), 0, 2)

        # Row 1
        grid.addWidget(self.createSplitIntoFilesButton(), 1, 0)
        grid.addWidget(self.createRebuildMonolithButton(), 1, 1)
        grid.addWidget(self.createPackageModuleButton(), 1, 2)

        self.setLayout(grid)

    # --- Button factories (visual only, no signals) ---

    def createCreateNewModuleButton(self) -> QPushButton:
        btn = QPushButton("Create New Module", self)
        btn.setObjectName("createModuleButton")
        btn.setIcon(qta.icon("fa5s.folder-plus", color="#333333"))
        btn.setIconSize(QSize(18, 18))
        btn.setMinimumHeight(40)
        btn.setStyleSheet(
            "background-color: #4A90E2; border-radius: 8px; padding: 8px; color: black;"
        )
        btn.clicked.connect(self._onCreateModuleClicked)
        return btn

    def createGenerateFromSpecButton(self) -> QPushButton:
        btn = QPushButton("Generate from Spec", self)
        btn.setObjectName("generateFromSpecButton")
        btn.setIcon(qta.icon("fa5s.file-alt", color="#333333"))
        btn.setIconSize(QSize(18, 18))
        btn.setMinimumHeight(40)
        btn.setStyleSheet(
            "background-color: #50C878; border-radius: 8px; padding: 8px; color: black;"
        )
        return btn

    def createRunTestsGlobalButton(self) -> QPushButton:
        btn = QPushButton("Run Tests (Global)", self)
        btn.setObjectName("runTestsGlobalButton")
        btn.setIcon(qta.icon("fa5s.vial", color="#333333"))
        btn.setIconSize(QSize(18, 18))
        btn.setMinimumHeight(40)
        btn.setStyleSheet(
            "background-color: #FFD700; border-radius: 8px; padding: 8px; color: black;"
        )
        return btn

    def createSplitIntoFilesButton(self) -> QPushButton:
        btn = QPushButton("Split into Files", self)
        btn.setObjectName("splitIntoFilesButton")
        btn.setIcon(qta.icon("fa5s.cut", color="#333333"))
        btn.setIconSize(QSize(18, 18))
        btn.setMinimumHeight(40)
        btn.setStyleSheet(
            "background-color: #FFA500; border-radius: 8px; padding: 8px; color: black;"
        )
        return btn

    def createRebuildMonolithButton(self) -> QPushButton:
        btn = QPushButton("Rebuild Monolith", self)
        btn.setObjectName("rebuildMonolithButton")
        btn.setIcon(qta.icon("fa5s.puzzle-piece", color="#333333"))
        btn.setIconSize(QSize(18, 18))
        btn.setMinimumHeight(40)
        btn.setStyleSheet(
            "background-color: #40E0D0; border-radius: 8px; padding: 8px; color: black;"
        )
        return btn

    def createPackageModuleButton(self) -> QPushButton:
        btn = QPushButton("Package Module", self)
        btn.setObjectName("packageModuleButton")
        btn.setIcon(qta.icon("fa5s.box", color="#333333"))
        btn.setIconSize(QSize(18, 18))
        btn.setMinimumHeight(40)
        btn.setStyleSheet(
            "background-color: #9370DB; border-radius: 8px; padding: 8px; color: black;"
        )
        return btn

    def _onCreateModuleClicked(self) -> None:
        dialog = CreateModuleDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Ici tu pourras ajouter le rafraîchissement de l’explorateur de fichiers
            pass
