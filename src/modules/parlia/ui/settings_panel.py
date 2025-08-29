from __future__ import annotations

import json
from typing import Any, Callable, Optional, cast

import qtawesome as qta
from PySide6.QtCore import Qt, QTimer, QUrl, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from modules.parlia.core.app_state_manager import AppStateManager
from modules.parlia.i18n.parlia_strings import ParliaStrings
from modules.parlia.services import parlia_data
from modules.parlia.ui.dialogs.settings_preferences_dialog import PreferencesDialog
from src.core.logger_manager import get_logger
from src.modules.parlia.services.ia_server_service import IaServerService, ia_server_service
from src.modules.parlia.services.ia_server_types import StatusResponse

logger = get_logger("SettingsPanel")


class SettingsPanel(QWidget):
    """Panneau des statuts et préférences.

    Intégration AppStateManager :
      - Reçoit les snapshots WS, les transmet au StateManager (source de vérité côté client).
      - Met l'UI à jour sur les signaux du StateManager (servicesUpdated/serviceStatusChanged).
      - Optimisme contrôlé lors d'une sélection de modèle Whisper (HTTP) pour bloquer l'enregistrement
        tant que le WS ne confirme pas (voir _initWhisperSelection).
    """

    def __init__(
        self,
        update_record_callback: Optional[Callable[[], None]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.update_record_callback = update_record_callback

        # Façade unique
        self.iaServerService: IaServerService = ia_server_service

        # StateManager (singleton)
        self.stateManager = AppStateManager()

        # Cache dernier statut WS (brut)
        self._lastStatus: Optional[StatusResponse] = None
        self.lastWhisperSelect: Optional[dict[str, Any]] = None

        # UI
        self._buildUi()
        self._connectStateSignals()
        self._applyInitialUiFromState()
        self._loadStyles()

        # WebSocket statut serveur
        self.socket = QWebSocket()
        self.socket.connected.connect(self._onConnected)
        self.socket.disconnected.connect(self._onDisconnected)
        self.socket.textMessageReceived.connect(self._onMessage)
        self._wsUrl: str = self._computeWsUrl()
        self._openSocket()

        # Sélection Whisper sauvegardée (synchrone HTTP, évènement WS attendu ensuite)
        self._initWhisperSelection()

    # --- Construction UI ---

    def _buildUi(self) -> None:
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self._addHeader()

        self.blocks_layout = QHBoxLayout()

        server_block = self._createServerBlock()
        whisper_block = self._createWhisperBlock()
        code_assistant_block = self._createCodeAssistantBlock()

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
        widget = QWidget()
        layout = QVBoxLayout(widget)

        title = QLabel("🖥️ Serveur IA")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        ollama_row = QHBoxLayout()
        ollama_label = QLabel("Ollama :")
        ollama_label.setStyleSheet("color: white; font-weight: bold;")
        ollama_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.serverOllamaValue = JLabelColored("Inconnu")
        ollama_row.addWidget(ollama_label)
        ollama_row.addWidget(self.serverOllamaValue)
        ollama_row.addStretch()
        layout.addLayout(ollama_row)

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

    # --- Connexions / StateManager ---

    def _connectStateSignals(self) -> None:
        # Mises à jour globales des services
        self.stateManager.servicesUpdated.connect(self._onServicesUpdated)
        # Si besoin d'un rafraîchissement fin par service :
        self.stateManager.serviceStatusChanged.connect(self._onServiceStatusChanged)

    def _applyInitialUiFromState(self) -> None:
        # Applique les infos déjà connues (par ex. si SettingsPanel est créé après premières updates)
        services = {k: v.toDict() for k, v in self.stateManager.services().items()}
        self._renderServices(services)

    def _loadStyles(self) -> None:
        # Styles externes (si nécessaire). Ici on garde simple pour éviter les dépendances circulaires.
        try:
            from modules.parlia.utils.stylesheet_loader import load_qss_for

            load_qss_for(self)
        except Exception:
            pass

    # --- Rendu UI à partir des services ---

    @Slot(dict)
    def _onServicesUpdated(self, services: dict[str, Any]) -> None:
        self._renderServices(services)

    @Slot(str, dict)
    def _onServiceStatusChanged(self, name: str, status: dict[str, Any]) -> None:
        # Mise à jour ciblée si besoin (ici on rerend tout pour simplicité et cohérence de couleurs)
        self._renderServices({k: v.toDict() for k, v in self.stateManager.services().items()})

    def _renderServices(self, services: dict[str, Any]) -> None:
        """Met à jour les trois blocs (Serveur, Whisper Model, Code Model) à partir d'un snapshot services."""
        try:
            whisper = cast(dict[str, Any], services.get("whisper", {}))
            ollama = cast(dict[str, Any], services.get("ollama", {}))
        except Exception:
            whisper, ollama = {}, {}

        # ---- Préparer un modèle affichable, robuste aux snapshots partiels ----
        # 1) On privilégie la clé aplatie "model" (maintenue par AppStateManager.updateService/applyServerSnapshot)
        # 2) Sinon on tente services.whisper.models.current (si jamais transmis brut par le serveur)
        # 3) Sinon "—"
        models_dict = (
            cast(dict[str, Any], whisper.get("models", {}))
            if isinstance(whisper.get("models"), dict)
            else {}
        )
        display_model = cast(str, whisper.get("model") or models_dict.get("current") or "—")

        # ---- Bloc Serveur: Whisper ----
        w_state = str(whisper.get("state", "")).lower()
        w_available = bool(whisper.get("available", False))
        w_ready = bool(whisper.get("ready", False))
        if w_state in ("loading", "starting", "pending"):
            self._setStatus(self.serverWhisperValue, "en attente", "warning")
        elif w_ready and w_available:
            self._setStatus(self.serverWhisperValue, "prêt", "ready")
        elif w_state == "error":
            self._setStatus(self.serverWhisperValue, "erreur", "error")
        else:
            self._setStatus(self.serverWhisperValue, "non disponible", "neutral")

        # ---- Bloc Serveur: Ollama ----
        o_state = str(ollama.get("state", "")).lower()
        o_available = bool(ollama.get("available", False))
        o_ready = bool(ollama.get("ready", False))
        if o_available:
            if o_state in ("ready", "running", "idle") or o_ready:
                self._setStatus(self.serverOllamaValue, "prêt", "ready")
            elif o_state in ("starting", "loading", "pending"):
                self._setStatus(self.serverOllamaValue, "en attente", "warning")
            elif o_state == "error":
                self._setStatus(self.serverOllamaValue, "erreur", "error")
            else:
                self._setStatus(self.serverOllamaValue, "en attente", "warning")
        else:
            self._setStatus(self.serverOllamaValue, "en attente", "warning")

        # ---- Bloc Whisper Model ----
        if w_state == "ready" and w_ready:
            self._setStatus(self.whisperModelValue, display_model, "ready")
        elif w_state in ("loading", "starting", "pending"):
            # Si on connaît déjà le modèle ciblé, on l'affiche en mode 'chargement…'
            if display_model != "—":
                self._setStatus(self.whisperModelValue, f"{display_model} (chargement…)", "warning")
            else:
                self._setStatus(self.whisperModelValue, "chargement…", "warning")
        elif w_state == "error":
            self._setStatus(self.whisperModelValue, display_model, "error")
        else:
            self._setStatus(self.whisperModelValue, "—", "neutral")

        # ---- Bloc Code Model ----
        selected_code = parlia_data.get_code_model()
        if o_ready and selected_code:
            self._setStatus(self.codeModelValue, selected_code, "ready")
        elif not o_available:
            self._setStatus(self.codeModelValue, selected_code or "—", "neutral")
        else:
            self._setStatus(self.codeModelValue, selected_code or "—", "neutral")

    # --- Actions UI ---

    def openPreferences(self) -> None:
        dlg = PreferencesDialog(self, iaServerService=self.iaServerService)
        dlg.setModelSelectedCallback(self._afterModelSelected)
        dlg.exec_()

    # --- Helpers statut → couleurs ---

    def _setStatus(self, value_label: QLabel, text: str, status_type: str) -> None:
        # couleurs simples pour feedback visuel
        colors: dict[str, str] = {
            "ready": "green",
            "error": "red",
            "warning": "orange",
            "neutral": "gray",
        }
        color = colors.get(status_type, "white")
        value_label.setText(text)
        value_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    # --- WebSocket helpers ---

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
        logger.debug(f"📩 WS message brut: {message}")
        try:
            dataAny: Any = json.loads(message)
            logger.debug(f"📩 WS data parsed: {dataAny}")
            if not isinstance(dataAny, dict):
                return

            # Snapshot complet du statut
            if "services" in dataAny and isinstance(dataAny["services"], dict):
                self._lastStatus = cast(StatusResponse, dataAny)
                # 1) Propager au StateManager (source de vérité)
                # NOTE: AppStateManager ne conserve pas le sous-dict "models".
                #       Il conserve cependant la clé aplatie "model". Assurons-nous côté serveur d'envoyer
                #       au moins "model", sinon on dépendra de l'optimisme local (updateService) et du fallback ci-dessus.
                self.stateManager.applyServerSnapshot(cast(dict[str, Any], dataAny["services"]))
                # 2) L'UI sera réactualisée via _onServicesUpdated
        except Exception as e:
            logger.error("Erreur parsing WS: %s", e)

    # --- Callbacks ---

    def _afterModelSelected(self) -> None:
        # Callback fourni par PreferencesDialog (après sélection modèle). On le relaie si fourni.
        if self.update_record_callback:
            self.update_record_callback()

    # --- Init sélection Whisper ---

    def _initWhisperSelection(self) -> None:
        saved = parlia_data.get_whisper_model()
        if not saved:
            return
        # envoi au serveur, l’UI sera mise à jour par WS ensuite
        try:
            info = self.iaServerService.whisper.selectModel(saved)
            self.lastWhisperSelect = info or {}
            # Optimisme contrôlé: marquer Whisper en loading pour verrouiller l'app jusqu'au snapshot suivant.
            try:
                self.stateManager.updateService(
                    "whisper", {"available": True, "state": "loading", "model": saved}
                )
            except Exception:
                pass
            self._setStatus(self.whisperModelValue, "chargement…", "warning")
        except Exception as e:
            logger.warning("Sélection Whisper initiale échouée: %s", e)

    # --- Lifecycle ---

    def closeEvent(self, event: QCloseEvent) -> None:
        try:
            self.socket.close()
        except Exception:
            pass
        super().closeEvent(event)


# --- QLabel colorable ---
class JLabelColored(QLabel):
    def __init__(self, text: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setStyleSheet("color: gray; font-weight: bold;")
