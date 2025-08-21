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


import time
from typing import Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from modules.parlia import ModuleInfo
from modules.parlia.services import parlia_data
from modules.parlia.services.parlia_data import get_max_duration
from modules.parlia.services.parlia_state_manager import parlia_state
from modules.parlia.ui.action_panel import ActionPanel
from modules.parlia.ui.fileTree_panel import FileTreePanel
from modules.parlia.ui.settings_panel import SettingsPanel

# from modules.parlia.ui.transcription_panel import TranscriptionPanel
from modules.parlia.utils import hotkeys
from modules.trakia.ui.tracker_widget import TrackerWidgetPanel
from src.core.logger_manager import get_logger
from src.modules.parlia.ui.transcription.transcription_panel import TranscriptionPanel

logger = get_logger("ParliaHome")


class HomePanel(QWidget):
    def __init__(self, main_window: Optional[QMainWindow] = None):
        super().__init__()
        self.main_window = main_window
        self.module_name = "parlia"
        logger.info("[UI] Initialisation du panneau d'accueil Parlia")

        # Initialisation de l'état
        self.selected_files: list[Any] = []

        # Construction de l'UI
        self._build_ui()

        # Connexion des hotkeys
        hotkeys.start_hotkey_listener(
            get_main_window=lambda: self.main_window,
            get_transcription_panel=lambda: self.transcription_panel,
        )

    def _build_ui(self) -> None:
        start = time.perf_counter()
        splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # Sidebar gauche : FileTreePanel
        self.file_tree_panel = FileTreePanel(root_path=".")
        self.file_tree_panel.files_selected.connect(self._on_files_selected)
        splitter.addWidget(self.file_tree_panel)

        # Conteneur droit : contenu existant
        right_container = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 10, 30, 10)
        layout.setSpacing(10)

        t0 = time.perf_counter()
        header_row = self._create_title_and_tracker_row()
        logger.debug(f"[PERF] build title/tracker : {time.perf_counter() - t0:.3f}s")
        separator1 = self._create_separator()
        t0 = time.perf_counter()
        transcription_block = self._create_transcription_block()
        logger.debug(f"[PERF] build transcription : {time.perf_counter() - t0:.3f}s")
        t0 = time.perf_counter()
        settings_block = self._create_settings_block()
        logger.debug(f"[PERF] build settings : {time.perf_counter() - t0:.3f}s")
        separator2 = self._create_separator()
        separator3 = self._create_separator()
        t0 = time.perf_counter()
        action_block = self._create_action_block()
        logger.debug(f"[PERF] build action : {time.perf_counter() - t0:.3f}s")

        layout.addWidget(header_row)
        layout.addWidget(separator1)
        layout.addWidget(settings_block)
        layout.addWidget(separator2)
        layout.addWidget(transcription_block)
        layout.addWidget(separator3)
        layout.addWidget(action_block)
        layout.addStretch()

        right_container.setLayout(layout)
        splitter.addWidget(right_container)

        # Définir le splitter comme layout principal
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        logger.debug(f"[PERF] Total build UI : {time.perf_counter() - start:.3f}s")

    def _create_title_and_tracker_row(self) -> QWidget:
        """
        Crée une ligne avec le titre centré et le widget Tracker à droite.
        """
        container = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 5)  # Réduction de la marge inférieure

        # Spacer gauche
        layout.addItem(QSpacerItem(40, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # Titre centré
        self.title = QLabel(f"{ModuleInfo.name}")
        self.title.setFont(QFont("Arial", 22, QFont.Weight.Normal))  # Taille réduite et Normal
        layout.addWidget(self.title)

        # Spacer centre (entre le titre et le tracker)
        layout.addItem(QSpacerItem(40, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

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

        self.settings_panel = SettingsPanel()
        layout.addWidget(self.settings_panel)

        container.setLayout(layout)
        return container

    def _create_transcription_block(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.transcription_panel = TranscriptionPanel(self)
        parlia_data.set_max_duration(int(get_max_duration()))
        layout.addWidget(self.transcription_panel)

        container.setLayout(layout)
        return container

    def _create_action_block(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.action_panel = ActionPanel(transcription_panel=self.transcription_panel, parent=self)
        layout.addWidget(self.action_panel)

        container.setLayout(layout)
        return container

    def _on_files_selected(self, file_list):
        """Met à jour la liste des fichiers sélectionnés."""
        self.selected_files = file_list
        logger.info(f"[UI] Fichiers sélectionnés : {self.selected_files}")

    def get_selected_files(self):
        """Retourne la liste des fichiers sélectionnés."""
        return self.selected_files

    def cleanup(self):
        if hasattr(self, "file_tree_panel"):
            self.file_tree_panel.files_selected.disconnect(self._on_files_selected)
        if hasattr(self, "transcription_panel"):
            parlia_state.unregister_ui_component(self.transcription_panel)
        if hasattr(self, "action_panel"):
            parlia_state.unregister_ui_component(self.action_panel)
        if hasattr(self, "settings_panel"):
            parlia_state.unregister_ui_component(self.settings_panel)

    def apply_ui_state(self):
        # logique spécifique pour mettre à jour ce panel
        logger.info(f"[UI] Mise à jour de {self.objectName()}")
