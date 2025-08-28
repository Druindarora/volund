# settings_panel.py
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

from modules.parlia.i18n.parlia_strings import ParliaStrings
from modules.parlia.services import parlia_data
from modules.parlia.ui.dialogs.settings_preferences_dialog import PreferencesDialog
from modules.parlia.utils.stylesheet_loader import load_qss_for
from src.core.logger_manager import get_logger
from src.modules.parlia.services.ia_server_service import IaServerService, ia_server_service
from src.modules.parlia.services.ia_server_types import StatusResponse

logger = get_logger("SettingsPanel")


class SettingsPanel(QWidget):
    def __init__(
        self,
        update_record_callback: Optional[Callable[[], None]] = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.update_record_callback = update_record_callback

        # Façade unique
        self.iaServerService: IaServerService = ia_server_service

        # Cache dernier statut WS
        self._lastStatus: Optional[StatusResponse] = None
        self.lastWhisperSelect: Optional[dict[str, Any]] = None

        # UI
        self._buildUi()
        load_qss_for(self)

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

    # --- Actions ---

    def openPreferences(self) -> None:
        dlg = PreferencesDialog(self, iaServerService=self.iaServerService)
        dlg.setModelSelectedCallback(self._afterModelSelected)
        dlg.exec_()

    # --- Mises à jour de statut ---

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

    def _updateServerStatus(self) -> None:
        if self._lastStatus is None:
            return
        status = self._lastStatus

        # Ollama
        try:
            oll = status["services"]["ollama"]
            oll_available = bool(oll["available"])
            if oll_available:
                state = (oll["state"] or "").lower()
                if state in ("ready", "running", "idle"):
                    self._setStatus(self.serverOllamaValue, "prêt", "ready")
                elif state in ("starting", "loading", "pending"):
                    self._setStatus(self.serverOllamaValue, "en attente", "warning")
                else:
                    self._setStatus(self.serverOllamaValue, "erreur", "error")
            else:
                self._setStatus(self.serverOllamaValue, "en attente", "warning")
        except Exception as e:
            logger.error("Erreur update serveur (Ollama): %s", e)
            self._setStatus(self.serverOllamaValue, "Injoignable", "error")

        # Whisper
        try:
            wh = status["services"]["whisper"]
            logger.debug(f"[Whisper] state={wh.get('state')} available={wh.get('available')}")
            state = str(wh.get("state", "")).lower()
            available = bool(wh.get("available", False))

            if state in ("loading", "starting", "pending"):
                # Pendant un chargement on n'affiche PAS "non disponible"
                self._setStatus(self.serverWhisperValue, "en attente", "warning")
            elif state == "ready" and available:
                self._setStatus(self.serverWhisperValue, "prêt", "ready")
            elif state == "error":
                self._setStatus(self.serverWhisperValue, "erreur", "error")
            else:
                # Seulement si pas de loading et pas ready → "non disponible"
                self._setStatus(self.serverWhisperValue, "non disponible", "neutral")
        except Exception as e:
            logger.error("Erreur update serveur (Whisper): %s", e)
            self._setStatus(self.serverWhisperValue, "Injoignable", "error")

    def _updateWhisperStatus(self) -> None:
        if self._lastStatus is None:
            return
        status = self._lastStatus
        try:
            wh = status["services"]["whisper"]
            models = wh.get("models", {})
            current = (models.get("current") if isinstance(models, dict) else None) or "—"
            state = (wh.get("state") or "").lower()

            if state == "ready":
                self._setStatus(self.whisperModelValue, str(current), "ready")
            elif state in ("loading", "starting", "pending"):
                self._setStatus(self.whisperModelValue, f"{current} (chargement…)", "warning")
            elif state == "error":
                self._setStatus(self.whisperModelValue, str(current) or "—", "error")
            else:
                # fallback si vraiment pas d'état
                self._setStatus(self.whisperModelValue, "—", "neutral")

        except Exception as e:
            logger.error("Erreur update Whisper (modèle): %s", e)
            self._setStatus(self.whisperModelValue, "—", "neutral")

    def _updateCodeStatus(self) -> None:
        if self._lastStatus is None:
            return
        status = self._lastStatus
        try:
            selected = parlia_data.get_code_model()
            try:
                oll = status["services"]["ollama"]
                available = bool(oll["available"])
                state = (oll["state"] or "").lower() if available else ""
            except Exception:
                self._setStatus(self.codeModelValue, "Injoignable", "error")
                return

            if available and state in ("ready", "running", "idle") and selected:
                self._setStatus(self.codeModelValue, selected, "ready")
            elif not available:
                self._setStatus(self.codeModelValue, selected or "—", "neutral")
            else:
                self._setStatus(self.codeModelValue, selected or "—", "neutral")
        except Exception as e:
            logger.error("Erreur update Code (modèle): %s", e)
            self._setStatus(self.codeModelValue, "—", "neutral")

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
            if "services" in dataAny:
                self._lastStatus = cast(StatusResponse, dataAny)
                self._updateServerStatus()
                self._updateWhisperStatus()
                self._updateCodeStatus()
        except Exception as e:
            logger.error("Erreur parsing WS: %s", e)

    # --- Callbacks ---

    def _afterModelSelected(self) -> None:
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
