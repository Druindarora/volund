from __future__ import annotations

import qtawesome as qta
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from modules.parlia.i18n.parlia_strings import ParliaStrings
from modules.parlia.ui.dialogs.action_settings_dialog import ActionSettingsDialog
from src.modules.parlia.ui.action.macro_actions_widget import MacroActionsWidget
from src.modules.parlia.ui.action.micro_actions_widget import MicroActionsWidget
from src.modules.parlia.ui.action.transverse_actions_widget import TransverseActionsWidget


class ActionPanel(QWidget):
    def __init__(
        self,
        transcription_panel: QWidget | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.transcription_panel = transcription_panel
        self._buildUi()

    # --- UI ---

    def _buildUi(self) -> None:
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel(ParliaStrings.Home.ACTIONS_TITLE, self)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        gear_button = QToolButton(self)
        gear_button.setIcon(qta.icon("fa5s.cog", color="#E5E5E5"))
        gear_button.setToolTip("Open Action Settings")
        gear_button.setFixedSize(32, 32)
        gear_button.clicked.connect(self._openSettings)
        header_layout.addWidget(gear_button)

        self.main_layout.addLayout(header_layout)

        # Tabs
        self.tabs = QTabWidget(self)
        self.tabs.addTab(MacroActionsWidget(self), "Macro")
        self.tabs.addTab(MicroActionsWidget(self), "Micro")
        self.tabs.addTab(TransverseActionsWidget(self), "Transverse")

        self.main_layout.addWidget(self.tabs)

    # --- Actions ---

    def _openSettings(self) -> None:
        dlg = ActionSettingsDialog(self)
        dlg.exec()
