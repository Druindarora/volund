from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from modules.parlia import ModuleInfo
from modules.parlia.services import parlia_data
from modules.parlia.services.parlia_data import get_max_duration
from modules.parlia.services.parlia_state_manager import parlia_state
from modules.parlia.settings import ParliaSettings
from modules.parlia.ui.action_panel import ActionPanel
from modules.parlia.ui.settings_panel import SettingsPanel
from modules.parlia.ui.transcription_panel import TranscriptionPanel
from modules.parlia.utils import hotkeys


class ParliaHome(QWidget):
    def __init__(self, main_window: QMainWindow):
        super().__init__(main_window)
        print("[DEBUG] ✅ ParliaHome instancié")
        self.main_window = main_window
        self._build_ui()
        hotkeys.start_hotkey_listener(
            get_main_window=lambda: self.main_window,
            get_transcription_panel=lambda: self.transcription_panel,
        )

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Création préalable des blocs dans le bon ordre logique
        title = self._create_title()
        separator1 = self._create_separator()

        # On crée d'abord le bloc de transcription (nécessaire pour créer Settings ensuite)
        transcription_block = self._create_transcription_block()

        # Ensuite on peut créer SettingsPanel en lui passant le callback correct
        settings_block = self._create_settings_block()

        separator2 = self._create_separator()
        separator3 = self._create_separator()
        action_block = self._create_action_block()

        # On ajoute tout dans le bon ordre dans le layout
        layout.addWidget(title)
        layout.addWidget(separator1)
        layout.addWidget(settings_block)
        layout.addWidget(separator2)
        layout.addWidget(transcription_block)
        layout.addWidget(separator3)
        layout.addWidget(action_block)
        layout.addStretch()

        self.setLayout(layout)

    def _create_title(self) -> QLabel:
        title = QLabel(f"Bienvenue dans {ModuleInfo.name}")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title.setContentsMargins(0, 0, 0, 20)
        return title

    def _create_separator(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #666666; background-color: #666666; height: 1px;")
        return line

    def _create_settings_block(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        label = QLabel(ParliaSettings.LABEL_SETTINGS_TITLE)
        label.setFont(QFont("Arial", 14, QFont.Weight.Normal))
        layout.addWidget(label)

        # On passe le vrai callback ici
        self.settings_panel = SettingsPanel(
            update_record_callback=self.transcription_panel.update_record_button_state
        )
        layout.addWidget(self.settings_panel)

        container.setLayout(layout)
        return container

    def _create_transcription_block(self) -> QWidget:
        """
        Crée un bloc pour la transcription.
        """
        container = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        label = QLabel(ParliaSettings.LABEL_TRANSCRIPTION_TITLE)
        label.setFont(QFont("Arial", 14, QFont.Weight.Normal))
        layout.addWidget(label)

        self.transcription_panel = TranscriptionPanel(self)
        parlia_data.set_max_duration(int(get_max_duration()))
        layout.addWidget(self.transcription_panel)

        container.setLayout(layout)
        return container

    def _create_action_block(self) -> QWidget:
        """
        Crée un bloc pour les actions.
        """
        container = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Placeholder pour le contenu futur
        label = QLabel(ParliaSettings.LABEL_ACTIONS_TITLE)
        label.setFont(QFont("Arial", 14, QFont.Weight.Normal))
        layout.addWidget(label)

        self.action_panel = ActionPanel(
            transcription_panel=self.transcription_panel, parent=self
        )
        layout.addWidget(self.action_panel)

        container.setLayout(layout)
        return container

    def cleanup(self):
        if hasattr(self, "transcription_panel"):
            parlia_state.unregister_ui_component(self.transcription_panel)
        if hasattr(self, "action_panel"):
            parlia_state.unregister_ui_component(self.action_panel)
        if hasattr(self, "settings_panel"):
            parlia_state.unregister_ui_component(self.settings_panel)
