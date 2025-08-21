# settings_panel.py

import threading
from typing import Any, Optional

import qtawesome as qta
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from modules.parlia.i18n.parlia_strings import ParliaStrings
from modules.parlia.services import parlia_data
from modules.parlia.services.ia_server_service import IaServerService
from modules.parlia.ui.dialogs.settings_preferences_dialog import PreferencesDialog
from modules.parlia.utils.stylesheet_loader import load_qss_for
from src.core.logger_manager import get_logger
from src.modules.parlia.services.ia_server_ollama_service import IaServerOllamaService
from src.modules.parlia.services.ia_server_whisper_service import IaServerWhisperService

logger = get_logger("SettingsPanel")


class SettingsPanel(QWidget):
    def __init__(self, update_record_callback=None, parent=None):
        super().__init__(parent)
        self.update_record_callback = update_record_callback

        # Service unique IA
        self.iaServerService = IaServerService("http://192.168.0.25:8000")
        self.iaServerWhisperService = IaServerWhisperService("http://192.168.0.25:8000")
        self.iaServerOllamaService = IaServerOllamaService("http://192.168.0.25:8000")

        # État local pour la sélection Whisper
        self.lastWhisperSelect: Optional[dict[str, Any]] = (
            None  # contient potentiellement {state,current,requested}
        )
        self.whisperPollingTimer = QTimer(self)
        self.whisperPollingTimer.setInterval(1500)
        self.whisperPollingTimer.timeout.connect(self._pollWhisperReady)

        # UI
        self._buildUi()
        load_qss_for(self)

        # Init statuts (unique point d’entrée)
        self._refreshStatusAndApply()

        # Sélectionne le modèle Whisper sauvegardé au démarrage (sans bloquer l'UI)
        self._initWhisperSelection()

    # --- Construction UI ---

    def _buildUi(self) -> None:
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self._addHeader()

        self.blocks_layout = QHBoxLayout()

        server_block = self._createServerBlock()  # 1) Serveur IA
        whisper_block = self._createWhisperBlock()  # 2) Whisper
        code_assistant_block = self._createCodeAssistantBlock()  # 3) Assistant codage

        self.blocks_layout.addWidget(server_block)
        self.blocks_layout.addWidget(whisper_block)
        self.blocks_layout.addWidget(code_assistant_block)

        self.main_layout.addLayout(self.blocks_layout)

        server_block.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        whisper_block.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        code_assistant_block.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

    def _addHeader(self) -> None:
        header_layout = QHBoxLayout()

        title_label = QLabel(ParliaStrings.Home.SETTINGS_TITLE, self)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        gear_button = QToolButton(self)
        gear_button.setIcon(qta.icon("fa5s.cog", color="#E5E5E5"))
        gear_button.setToolTip("Ouvrir les préférences")
        gear_button.setFixedSize(32, 32)
        gear_button.clicked.connect(self.openPreferences)
        header_layout.addWidget(gear_button)

        self.main_layout.addLayout(header_layout)

    # --- Blocs ---

    def _createServerBlock(self) -> QWidget:
        """Bloc d'état global du serveur IA (Ollama + Whisper)."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("🖥️ Serveur IA")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        # Ligne Ollama
        ollama_row = QHBoxLayout()
        ollama_label = QLabel("Ollama :")
        ollama_label.setStyleSheet("color: white; font-weight: bold;")
        ollama_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.serverOllamaValue = JLabelColored("Inconnu")
        ollama_row.addWidget(ollama_label)
        ollama_row.addWidget(self.serverOllamaValue)
        ollama_row.addStretch()
        layout.addLayout(ollama_row)

        # Ligne Whisper
        whisper_row = QHBoxLayout()
        whisper_label = QLabel("Whisper :")
        whisper_label.setStyleSheet("color: white; font-weight: bold;")
        whisper_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.serverWhisperValue = JLabelColored("Inconnu")
        whisper_row.addWidget(whisper_label)
        whisper_row.addWidget(self.serverWhisperValue)
        whisper_row.addStretch()
        layout.addLayout(whisper_row)

        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        return widget

    def _createWhisperBlock(self) -> QWidget:
        """Bloc modèle Whisper."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("🎤 Modèle Whisper")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        row = QHBoxLayout()
        static_label = QLabel("Modèle sélectionné :")
        static_label.setStyleSheet("color: white; font-weight: bold;")
        static_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)

        self.whisperModelValue = JLabelColored("—")
        row.addWidget(static_label)
        row.addWidget(self.whisperModelValue)
        row.addStretch()
        layout.addLayout(row)

        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        return widget

    def _createCodeAssistantBlock(self) -> QWidget:
        """Bloc modèle Assistant de codage (dépend d’Ollama)."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("💻 Assistant de codage")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        row = QHBoxLayout()
        static_label = QLabel("Modèle sélectionné :")
        static_label.setStyleSheet("color: white; font-weight: bold;")
        static_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)

        self.codeModelValue = JLabelColored("—")
        row.addWidget(static_label)
        row.addWidget(self.codeModelValue)
        row.addStretch()
        layout.addLayout(row)

        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        return widget

    # --- Actions ---

    def openPreferences(self) -> None:
        """Ouvre le PreferencesDialog en lui injectant IaServerService."""
        dlg = PreferencesDialog(self, iaServerService=self.iaServerService)
        dlg.setModelSelectedCallback(self._afterModelSelected)
        dlg.exec_()

    # --- Mises à jour de statut ---

    def _setStatus(self, value_label: QLabel, text: str, status_type: str) -> None:
        """MAJ couleur + texte du label de statut."""
        colors = {
            "ready": "green",
            "error": "red",
            "warning": "orange",
            "neutral": "gray",
        }
        color = colors.get(status_type, "white")
        value_label.setText(text)
        value_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def _refreshStatusAndApply(self) -> None:
        """Rafraîchit /status puis met à jour tous les blocs."""
        try:
            self.iaServerService.refreshStatus()
        except Exception as e:
            # Serveur injoignable : on affiche l’état rouge partout pertinent
            logger.error("Échec refreshStatus dans SettingsPanel: %s", e)
            self._setStatus(self.serverOllamaValue, "Injoignable", "error")
            self._setStatus(self.serverWhisperValue, "Injoignable", "error")
            self._setStatus(self.whisperModelValue, "—", "neutral")
            self._setStatus(self.codeModelValue, "Injoignable", "error")
            return

        self._updateServerStatus()
        self._updateWhisperStatus()
        self._updateCodeStatus()

    def _updateServerStatus(self) -> None:
        """Met à jour les lignes Ollama/Whisper du bloc Serveur IA."""
        # Ollama
        try:
            ollama_available = bool(self.iaServerService.getOllamaAvailable())
            if ollama_available:
                state = (self.iaServerService.getOllamaState() or "").lower()
                if state in ("ready", "running", "idle"):
                    self._setStatus(self.serverOllamaValue, "prêt", "ready")
                elif state in ("starting", "loading", "pending"):
                    self._setStatus(self.serverOllamaValue, "en attente", "warning")
                else:
                    self._setStatus(self.serverOllamaValue, "erreur", "error")
            else:
                # Non lancé / pas disponible
                self._setStatus(self.serverOllamaValue, "en attente", "warning")
        except Exception as e:
            logger.error("Erreur update serveur (Ollama): %s", e)
            self._setStatus(self.serverOllamaValue, "Injoignable", "error")

        # Whisper
        try:
            whisper_available = bool(self.iaServerService.getWhisperAvailable())
            if whisper_available:
                state = (self.iaServerService.getWhisperState() or "").lower()
                if state in ("ready", "running", "idle"):
                    self._setStatus(self.serverWhisperValue, "prêt", "ready")
                else:
                    # Spécification: pas d’“en attente” pour Whisper dans ce bloc
                    self._setStatus(self.serverWhisperValue, "erreur", "error")
            else:
                self._setStatus(self.serverWhisperValue, "non disponible", "neutral")
        except Exception as e:
            logger.error("Erreur update serveur (Whisper): %s", e)
            self._setStatus(self.serverWhisperValue, "Injoignable", "error")

    def _updateWhisperStatus(self) -> None:
        """Bloc 2 : affiche le modèle Whisper sélectionné et l’état de chargement."""
        try:
            if self.iaServerService.getWhisperAvailable():
                current = self.iaServerService.getCurrentWhisperModel() or "—"
                state = (self.iaServerService.getWhisperState() or "").lower()
                requested = ""
                if self.lastWhisperSelect:
                    req = self.lastWhisperSelect.get("requested")
                    if isinstance(req, str):
                        requested = req

                if state == "loading" and requested and requested != current:
                    # Affiche "current (chargement → requested)" en orange
                    self._setStatus(
                        self.whisperModelValue,
                        f"{current} (chargement → {requested})",
                        "warning",
                    )
                    self._startWhisperPolling()
                elif state == "ready":
                    self._setStatus(self.whisperModelValue, current, "ready")
                    self._stopWhisperPolling()
                else:
                    self._setStatus(self.whisperModelValue, current or "—", "neutral")
            else:
                self._setStatus(self.whisperModelValue, "—", "neutral")
        except Exception as e:
            logger.error("Erreur update Whisper (modèle): %s", e)
            self._setStatus(self.whisperModelValue, "—", "neutral")

    def _updateCodeStatus(self) -> None:
        """Bloc 3 : affiche le modèle de codage (vert si Ollama prêt + modèle sélectionné)."""
        try:
            selected = parlia_data.get_code_model()
            try:
                available = bool(self.iaServerService.getOllamaAvailable())
                state = (self.iaServerService.getOllamaState() or "").lower() if available else ""
            except Exception:
                # Injoignable
                self._setStatus(self.codeModelValue, "Injoignable", "error")
                return

            if available and state in ("ready", "running", "idle") and selected:
                self._setStatus(self.codeModelValue, selected, "ready")
            elif not available:
                self._setStatus(self.codeModelValue, selected or "—", "neutral")
            else:
                # Ollama dispo mais pas prêt, ou pas de modèle sélectionné
                self._setStatus(self.codeModelValue, selected or "—", "neutral")
        except Exception as e:
            logger.error("Erreur update Code (modèle): %s", e)
            self._setStatus(self.codeModelValue, "—", "neutral")

    # --- Callbacks ---

    def _afterModelSelected(self):
        """Callback déclenché depuis PreferencesDialog après sélection modèle."""
        self._refreshStatusAndApply()
        if self.update_record_callback:
            self.update_record_callback()

    # --- Init sélection Whisper + polling ---

    def _initWhisperSelection(self) -> None:
        """Lance la sélection du modèle Whisper sauvegardé, sans bloquer l'UI."""
        saved = parlia_data.get_whisper_model()
        if not saved:
            return
        # Lancer la requête POST en thread pour éviter de bloquer l'UI
        t = threading.Thread(target=self._asyncSelectWhisper, args=(saved,), daemon=True)
        t.start()
        # Démarre le polling immédiat (au cas où l'état passe à 'loading')
        self._startWhisperPolling()

    def _asyncSelectWhisper(self, modelName: str) -> None:
        """Thread: POST /whisper/select et mémorise la réponse."""
        try:
            info = self.iaServerService.selectWhisperModel(modelName)
            # Mémorise la dernière réponse (peut contenir state/current/requested)
            self.lastWhisperSelect = info or {}
        except Exception as e:
            logger.warning("selectWhisperModel a échoué: %s", e, exc_info=True)

    def _startWhisperPolling(self) -> None:
        """Démarre le polling périodique de /status jusqu'à 'ready'."""
        if not self.whisperPollingTimer.isActive():
            self.whisperPollingTimer.start()

    def _stopWhisperPolling(self) -> None:
        """Arrête le polling."""
        if self.whisperPollingTimer.isActive():
            self.whisperPollingTimer.stop()

    def _pollWhisperReady(self) -> None:
        """Tick de polling: rafraîchit les statuts et s'arrête si Whisper est prêt."""
        try:
            self.iaServerService.refreshStatus()
        except Exception as e:
            logger.error("Polling Whisper: refreshStatus a échoué: %s", e)
            # On laisse l'UI refléter l'état actuel
        self._updateServerStatus()
        self._updateWhisperStatus()
        self._updateCodeStatus()


# --- Petit helper pour instancier des QLabel colorables proprement ---
class JLabelColored(QLabel):
    def __init__(self, text: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setStyleSheet("color: gray; font-weight: bold;")
