# settings_panel.py

from typing import Any, Optional

import qtawesome as qta
from PySide6.QtCore import QObject, Qt, QThread, QTimer, Signal, Slot
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
from src.modules.parlia.services.ia_server_service import (
    IaServerService,
    StatusResponse,
    ia_server_service,
)

logger = get_logger("SettingsPanel")


class ServerWorker(QObject):
    statusFetched = Signal(dict)
    statusFailed = Signal(str)
    modelSelected = Signal(dict)

    def __init__(self, iaServerService: IaServerService) -> None:
        super().__init__()
        self.iaServerService = iaServerService
        self._statusInFlight = False

    @Slot()
    def fetchStatus(self) -> None:
        if self._statusInFlight:
            return
        self._statusInFlight = True
        try:
            data = self.iaServerService.refreshStatus()
            self.statusFetched.emit(data)
        except Exception as e:
            self.statusFailed.emit(str(e))
        finally:
            self._statusInFlight = False

    @Slot(str)
    def selectWhisperModel(self, modelName: str) -> None:
        try:
            info = self.iaServerService.whisper.selectModel(modelName)
            self.modelSelected.emit(info)
        except Exception as e:
            self.statusFailed.emit(str(e))


class SettingsPanel(QWidget):
    # signaux pour déclencher le worker (connexion inter-threads automatique)
    requestFetchStatus = Signal()
    requestSelectWhisperModel = Signal(str)

    def __init__(self, update_record_callback=None, parent=None):
        super().__init__(parent)
        self.update_record_callback = update_record_callback

        # Façade unique + sous-services partagés
        self.iaServerService = ia_server_service

        # Thread + worker réseau non bloquants
        self._workerThread = QThread(self)
        self._worker = ServerWorker(self.iaServerService)
        self._worker.moveToThread(self._workerThread)

        # Connexions worker → UI
        self._worker.statusFetched.connect(self._onStatusFetched)
        self._worker.statusFailed.connect(self._onStatusFailed)
        self._worker.modelSelected.connect(self._onModelSelected)

        # Connexions UI → worker (queued, thread-safe)
        self.requestFetchStatus.connect(self._worker.fetchStatus)
        self.requestSelectWhisperModel.connect(self._worker.selectWhisperModel)

        self._workerThread.start()

        # État local Whisper
        self.lastWhisperSelect: Optional[dict[str, Any]] = None
        self.whisperPollingTimer = QTimer(self)
        self.whisperPollingTimer.setInterval(3000)  # 3s
        self.whisperPollingTimer.timeout.connect(self._pollWhisperReady)

        # UI
        self._buildUi()
        load_qss_for(self)

        # Init statuts (asynchrone)
        self._refreshStatusAndApply()

        # Sélection Whisper sauvegardée (asynchrone)
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
        colors = {"ready": "green", "error": "red", "warning": "orange", "neutral": "gray"}
        color = colors.get(status_type, "white")
        value_label.setText(text)
        value_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def _refreshStatusAndApply(self) -> None:
        # asynchrone via worker
        self.requestFetchStatus.emit()

    def _status(self) -> StatusResponse:
        return self.iaServerService.getStatus()

    def _updateServerStatus(self) -> None:
        status = self._status()

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
            whisper_available = bool(wh["available"])
            if whisper_available:
                state = (wh["state"] or "").lower()
                if state in ("ready", "running", "idle"):
                    self._setStatus(self.serverWhisperValue, "prêt", "ready")
                else:
                    self._setStatus(self.serverWhisperValue, "erreur", "error")
            else:
                self._setStatus(self.serverWhisperValue, "non disponible", "neutral")
        except Exception as e:
            logger.error("Erreur update serveur (Whisper): %s", e)
            self._setStatus(self.serverWhisperValue, "Injoignable", "error")

    def _updateWhisperStatus(self) -> None:
        status = self._status()
        try:
            wh = status["services"]["whisper"]
            if wh["available"]:
                models = wh["models"]
                current = models["current"] or "—"
                state = (wh["state"] or "").lower()

                requested = ""
                if self.lastWhisperSelect:
                    req = self.lastWhisperSelect.get("requested")
                    if isinstance(req, str):
                        requested = req

                if state == "loading" and requested and requested != current:
                    self._setStatus(
                        self.whisperModelValue,
                        f"{current} (chargement → {requested})",
                        "warning",
                    )
                    self._startWhisperPolling()
                elif state == "ready":
                    self._setStatus(self.whisperModelValue, str(current), "ready")
                    self._stopWhisperPolling()
                else:
                    self._stopWhisperPolling()
                    self._setStatus(self.whisperModelValue, str(current) or "—", "neutral")
            else:
                self._setStatus(self.whisperModelValue, "—", "neutral")
        except Exception as e:
            logger.error("Erreur update Whisper (modèle): %s", e)
            self._setStatus(self.whisperModelValue, "—", "neutral")

    def _updateCodeStatus(self) -> None:
        status = self._status()
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

    # --- Slots worker → UI ---

    @Slot(dict)
    def _onStatusFetched(self, _data: dict[str, Any]) -> None:
        self._updateServerStatus()
        self._updateWhisperStatus()
        self._updateCodeStatus()

    @Slot(str)
    def _onStatusFailed(self, _msg: str) -> None:
        self._stopWhisperPolling()
        self._setStatus(self.serverOllamaValue, "Injoignable", "error")
        self._setStatus(self.serverWhisperValue, "Injoignable", "error")
        self._setStatus(self.whisperModelValue, "—", "neutral")
        self._setStatus(self.codeModelValue, "Injoignable", "error")

    @Slot(dict)
    def _onModelSelected(self, info: dict[str, Any]) -> None:
        self.lastWhisperSelect = info or {}
        self._updateWhisperStatus()
        self._startWhisperPolling()
        # déclenche un refresh async pour refléter l'état 'loading' → 'ready'
        self.requestFetchStatus.emit()

    # --- Callbacks ---

    def _afterModelSelected(self):
        self._refreshStatusAndApply()
        if self.update_record_callback:
            self.update_record_callback()

    # --- Init sélection Whisper + polling ---

    def _initWhisperSelection(self) -> None:
        saved = parlia_data.get_whisper_model()
        if not saved:
            return
        self.requestSelectWhisperModel.emit(saved)
        self._startWhisperPolling()

    def _startWhisperPolling(self) -> None:
        if not getattr(self, "_pollingScheduled", False):
            self._pollingScheduled = True
            QTimer.singleShot(3000, self._pollOnce)

    def _pollOnce(self) -> None:
        self._pollingScheduled = False
        self.requestFetchStatus.emit()

    def _stopWhisperPolling(self) -> None:
        if self.whisperPollingTimer.isActive():
            self.whisperPollingTimer.stop()

    def _pollWhisperReady(self) -> None:
        # tick → refresh async
        self.requestFetchStatus.emit()

    # --- Lifecycle ---

    def closeEvent(self, event):
        try:
            self._stopWhisperPolling()
            self._workerThread.quit()
            self._workerThread.wait()
        except Exception:
            pass
        super().closeEvent(event)


# --- QLabel colorable ---
class JLabelColored(QLabel):
    def __init__(self, text: str = "", parent: Optional[QWidget] = None) -> None:
        super().__init__(text, parent)
        self.setStyleSheet("color: gray; font-weight: bold;")
