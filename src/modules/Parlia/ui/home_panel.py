# === FICHIER : home_parlia.py ===
# 🔍 Audit du panneau d'accueil principal de Parlia
# --------------------------------------------------
# ✅ Rôle : point d'entrée UI, agencement des blocs principaux
# 📁 Composant central, bien localisé dans `ui/`
# --------------------------------------------------

# ✅ Points forts :
# - Structure propre, claire, logique verticale de l'UI
# - Instanciation des blocs dans des méthodes dédiées (_create_xxx)
# - Appels à `hotkeys.start_hotkey_listener()` et `parlia_data` bien encapsulés
# - Gestion du `parlia_state` à la fin avec `cleanup()`

# 🔄 Idées d'amélioration mineures :
# - Regrouper visuellement `settings` et `transcription` côte à côte si UI le permet
# - Ajouter une méthode `apply_ui_state()` ici si ce composant devient réactif à l'état (optionnel)
# - Séparer le `TrackerWidgetPanel` dans un layout plus logique si UI évolue vers une sidebar gauche

# 🟢 Verdict : rien à refactorer pour l’instant. Ce fichier sert uniquement de coordinateur UI.
# Tu peux t’appuyer dessus tel quel pour construire la suite (FilePanel, etc.).


from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSizePolicy,
    QSpacerItem,
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
from modules.trakia.ui.tracker_widget import TrackerWidgetPanel
from src.core.logger_manager import get_logger

logger = get_logger("ParliaHome")


class HomePanel(QWidget):
    def __init__(self, main_window: Optional[QMainWindow] = None):
        super().__init__()
        self.main_window = main_window
        setattr(self, "module_name", "parlia")  # 🔧 important
        logger.info("[UI] Initialisation du panneau d'accueil Parlia")
        self._build_ui()
        hotkeys.start_hotkey_listener(
            get_main_window=lambda: self.main_window,
            get_transcription_panel=lambda: self.transcription_panel,
        )

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        header_row = self._create_title_and_tracker_row()
        separator1 = self._create_separator()
        transcription_block = self._create_transcription_block()
        settings_block = self._create_settings_block()
        separator2 = self._create_separator()
        separator3 = self._create_separator()
        action_block = self._create_action_block()

        layout.addWidget(header_row)
        layout.addWidget(separator1)
        layout.addWidget(settings_block)
        layout.addWidget(separator2)
        layout.addWidget(transcription_block)
        layout.addWidget(separator3)
        layout.addWidget(action_block)
        layout.addStretch()

        self.setLayout(layout)

    def _create_title_and_tracker_row(self) -> QWidget:
        """
        Crée une ligne avec le titre centré et le widget Tracker à droite.
        """
        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 20)

        # Spacer gauche
        layout.addItem(
            QSpacerItem(40, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )

        # Titre centré
        self.title = QLabel(f"{ModuleInfo.name}")
        self.title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        layout.addWidget(self.title)

        # Spacer centre (entre le titre et le tracker)
        layout.addItem(
            QSpacerItem(40, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )

        # Widget Tracker à droite
        self.tracker_widget = TrackerWidgetPanel()
        layout.addWidget(self.tracker_widget)

        container.setLayout(layout)
        return container

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

        self.settings_panel = SettingsPanel(
            update_record_callback=self.transcription_panel.update_record_button_state
        )
        layout.addWidget(self.settings_panel)

        container.setLayout(layout)
        return container

    def _create_transcription_block(self) -> QWidget:
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
        container = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

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

    def apply_ui_state(self):
        # logique spécifique pour mettre à jour ce panel
        logger.info(f"[UI] Mise à jour de {self.objectName()}")
