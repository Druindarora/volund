# settings_panel.py
from __future__ import annotations

import json
from typing import Any, Callable, Optional, cast

import qtawesome as qta
from PySide6.QtCore import QTimer, QUrl, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from modules.parlia.core.app_state_manager import AppStateManager
from modules.parlia.services import parlia_data
from modules.parlia.ui.dialogs.settings_preferences_dialog import PreferencesDialog
from src.core.logger_manager import get_logger
from src.modules.parlia.i18n.parlia_strings import ParliaStrings
from src.modules.parlia.services.ia_server_service import IaServerService, ia_server_service
from src.modules.parlia.services.ia_server_types import StatusResponse

logger = get_logger("SettingsPanel")


class SettingsPanel(QWidget):
    """Section Paramètres : ligne unique Whisper + Ollama."""

    # labels (créés dans _buildUi)
    whisperStatusLabel: QLabel
    whisperModelLabel: QLabel
    ollamaStatusLabel: QLabel
    ollamaModelLabel: QLabel

    def __init__(
        self,
        update_record_callback: Optional[Callable[[], None]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.update_record_callback = update_record_callback

        self.iaServerService: IaServerService = ia_server_service
        self.stateManager = AppStateManager()

        self._lastStatus: Optional[StatusResponse] = None
        self.lastWhisperSelect: Optional[dict[str, Any]] = None

        self._buildUi()
        self._connectStateSignals()
        self._applyInitialUiFromState()
        self._loadStyles()

        # WebSocket
        self.socket = QWebSocket()
        self.socket.connected.connect(self._onConnected)
        self.socket.disconnected.connect(self._onDisconnected)
        self.socket.textMessageReceived.connect(self._onMessage)
        self._wsUrl: str = self._computeWsUrl()
        self._openSocket()

        self._initWhisperSelection()

    # --- UI ---

    def _buildUi(self) -> None:
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Ligne unique Paramètres
        self.params_layout = QHBoxLayout()

        # Libellé "Paramètres –"
        params_label = QLabel(ParliaStrings.Home.SETTINGS_TITLE, self)
        params_label.setStyleSheet("color: #E5E5E5; font-weight: bold;")
        self.params_layout.addWidget(params_label)

        # Whisper: <status> (<model>)
        self.whisperStatusLabel, self.whisperModelLabel = self._createInlineGroup("Whisper:")

        # Séparateur
        self._addDotSeparator()

        # Ollama: <status> (<model>)
        self.ollamaStatusLabel, self.ollamaModelLabel = self._createInlineGroup("Ollama:")

        # Spacer extensible pour pousser le bouton à droite
        self.params_layout.addStretch()

        # ⚙️ bouton préférences (fin de ligne, fixé à droite)
        self.paramsGearBtn = QToolButton(self)
        self.paramsGearBtn.setIcon(qta.icon("fa5s.cog", color="#E5E5E5"))
        self.paramsGearBtn.setToolTip("Ouvrir les préférences")
        self.paramsGearBtn.setFixedSize(24, 24)
        self.paramsGearBtn.clicked.connect(self.openPreferences)
        self.params_layout.addWidget(self.paramsGearBtn)

        self.main_layout.addLayout(self.params_layout)

    def _createInlineGroup(self, prefix: str) -> tuple[QLabel, QLabel]:
        """Crée '<prefix> <statusColored> (<model>)' et renvoie (status_label, model_label)."""
        prefix_label = QLabel(prefix, self)
        prefix_label.setStyleSheet("color: white; font-weight: bold;")
        self.params_layout.addWidget(prefix_label)

        status_label = QLabel("—", self)  # couleur via _setStatus
        self.params_layout.addWidget(status_label)

        model_label = QLabel("(—)", self)
        model_label.setStyleSheet("color: #E5E5E5;")
        self.params_layout.addWidget(model_label)

        return status_label, model_label

    def _addDotSeparator(self) -> None:
        sep = QLabel("·", self)
        sep.setStyleSheet("color: #A0A0A0; padding: 0 6px;")
        self.params_layout.addWidget(sep)

    def _loadStyles(self) -> None:
        try:
            from modules.parlia.utils.stylesheet_loader import load_qss_for

            load_qss_for(self)
        except Exception:
            pass

    # --- State wiring ---

    def _connectStateSignals(self) -> None:
        self.stateManager.servicesUpdated.connect(self._onServicesUpdated)
        self.stateManager.serviceStatusChanged.connect(self._onServiceStatusChanged)

    def _applyInitialUiFromState(self) -> None:
        services = {k: v.toDict() for k, v in self.stateManager.services().items()}
        self._renderServices(services)

    # --- Rendu ---

    @Slot(dict)
    def _onServicesUpdated(self, services: dict[str, Any]) -> None:
        self._renderServices(services)

    @Slot(str, dict)
    def _onServiceStatusChanged(self, _name: str, _status: dict[str, Any]) -> None:
        self._renderServices({k: v.toDict() for k, v in self.stateManager.services().items()})

    def _renderServices(self, services: dict[str, Any]) -> None:
        """Met à jour la ligne unique Paramètres (Whisper + Ollama)."""
        try:
            whisper = cast(dict[str, Any], services.get("whisper", {}))
            ollama = cast(dict[str, Any], services.get("ollama", {}))
        except Exception:
            whisper, ollama = {}, {}

        # Whisper
        w_state = str(whisper.get("state", "")).lower()
        w_available = bool(whisper.get("available", False))
        w_ready = bool(whisper.get("ready", False))
        w_models = whisper.get("models", {}) if isinstance(whisper.get("models"), dict) else {}
        w_model = cast(str, whisper.get("model") or w_models.get("current") or "—")

        if w_state in ("loading", "starting", "pending"):
            self._setStatus(self.whisperStatusLabel, "en attente", "warning")
        elif w_ready and w_available:
            self._setStatus(self.whisperStatusLabel, "prêt", "ready")
        elif w_state == "error":
            self._setStatus(self.whisperStatusLabel, "erreur", "error")
        else:
            self._setStatus(self.whisperStatusLabel, "non disponible", "neutral")
        self._setModelParen(self.whisperModelLabel, w_model)

        # Ollama (toujours afficher le modèle entre parenthèses)
        o_state = str(ollama.get("state", "")).lower()
        o_available = bool(ollama.get("available", False))
        o_ready = bool(ollama.get("ready", False))
        # modèle affiché = modèle "Assistant codage" persistant s'il existe, sinon modèle service
        selected_code = parlia_data.get_code_model()
        o_model_service = cast(str, ollama.get("model") or "—")
        o_model_display = selected_code or o_model_service

        if o_available:
            if o_state in ("ready", "running", "idle") or o_ready:
                self._setStatus(self.ollamaStatusLabel, "prêt", "ready")
            elif o_state in ("starting", "loading", "pending"):
                self._setStatus(self.ollamaStatusLabel, "en attente", "warning")
            elif o_state == "error":
                self._setStatus(self.ollamaStatusLabel, "erreur", "error")
            else:
                self._setStatus(self.ollamaStatusLabel, "en attente", "warning")
        else:
            self._setStatus(self.ollamaStatusLabel, "en attente", "warning")
        self._setModelParen(self.ollamaModelLabel, o_model_display or "—")

    # --- Actions ---

    def openPreferences(self) -> None:
        dlg = PreferencesDialog(self, iaServerService=self.iaServerService)
        dlg.setModelSelectedCallback(self._afterModelSelected)
        dlg.exec_()

    # --- Helpers ---

    def _setStatus(self, label: QLabel, text: str, status_type: str) -> None:
        # couleurs identiques à l’existant
        colors: dict[str, str] = {
            "ready": "green",
            "error": "red",
            "warning": "orange",
            "neutral": "gray",
        }
        label.setText(text)
        label.setStyleSheet(f"color: {colors.get(status_type, 'white')}; font-weight: bold;")

    def _setModelParen(self, label: QLabel, model: str) -> None:
        label.setText(f"({model or '—'})")

    # --- WebSocket ---

    def _computeWsUrl(self) -> str:
        base = getattr(self.iaServerService, "baseUrl", "http://127.0.0.1:8000")
        if base.startswith("https://"):
            return f"wss://{base[len('https://') :]}/ws/status"
        if base.startswith("http://"):
            return f"ws://{base[len('http://') :]}/ws/status"
        return f"ws://{base}/ws/status"

    def _openSocket(self) -> None:
        self.socket.open(QUrl(self._wsUrl))

    @Slot()
    def _onConnected(self) -> None:
        logger.info("✅ WebSocket connecté au serveur IA")

    @Slot()
    def _onDisconnected(self) -> None:
        logger.warning("⚠️ WebSocket déconnecté, tentative de reconnexion…")
        QTimer.singleShot(3000, self._openSocket)

    @Slot(str)
    def _onMessage(self, message: str) -> None:
        try:
            dataAny: Any = json.loads(message)
            if not isinstance(dataAny, dict):
                return
            if "services" in dataAny and isinstance(dataAny["services"], dict):
                self._lastStatus = cast(StatusResponse, dataAny)
                self.stateManager.applyServerSnapshot(cast(dict[str, Any], dataAny["services"]))
        except Exception as e:
            logger.error("Erreur parsing WS: %s", e)

    def _afterModelSelected(self) -> None:
        if self.update_record_callback:
            self.update_record_callback()

    def _initWhisperSelection(self) -> None:
        saved = parlia_data.get_whisper_model()
        if not saved:
            return
        try:
            info = self.iaServerService.whisper.selectModel(saved)
            self.lastWhisperSelect = info or {}
            # Optimisme : marquer loading, WS confirmera
            try:
                self.stateManager.updateService(
                    "whisper", {"available": True, "state": "loading", "model": saved}
                )
            except Exception:
                pass
        except Exception as e:
            logger.warning("Sélection Whisper initiale échouée: %s", e)

    # --- Lifecycle ---

    def closeEvent(self, event: QCloseEvent) -> None:
        try:
            self.socket.close()
        except Exception:
            pass
        super().closeEvent(event)


class JLabelColored(QLabel):
    def __init__(self, text: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setStyleSheet("color: gray; font-weight: bold;")
