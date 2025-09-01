# transcription_panel.py

from typing import Any, Optional

import qtawesome as qta
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from modules.parlia.core.app_state_manager import AppStateManager
from modules.parlia.i18n.parlia_strings import ParliaStrings
from modules.parlia.services.audioService import audio_service
from modules.parlia.ui.dialogs.transcription_settings_dialog import (
    TranscriptionSettingsDialog,
)
from modules.parlia.utils.stylesheet_loader import load_qss_for
from src.core.logger_manager import get_logger
from src.modules.parlia.services.ia_server_service import ia_server_service
from src.modules.parlia.ui.transcription.controls_panel import ControlsPanel
from src.modules.parlia.ui.transcription.conversation_panel import ConversationPanel

logger = get_logger("TranscriptionPanel")


class TranscriptionPanel(QWidget):
    """Orchestrateur : assemble ControlsPanel + ConversationPanel."""

    # Nouveau signal pour rapatrier les résultats de transcription
    transcriptionReady = Signal(dict)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.mainLayout = QVBoxLayout(self)
        self._addHeader()

        # Sous-panneaux
        self.controlsPanel = ControlsPanel(parent=self)

        # Connecter les signaux du ControlsPanel à l’orchestrateur
        self.controlsPanel.recordingStarted.connect(self._onRecordingStarted)
        self.controlsPanel.recordingStopped.connect(self._onRecordingStopped)
        self.controlsPanel.copyMessageRequested.connect(self._onCopyMessage)
        self.controlsPanel.copyResponseRequested.connect(self._onCopyResponse)

        self.conversationPanel = ConversationPanel(self)

        self.conversationPanel.copyMessageRequested.connect(self._onCopyMessage)

        contentRow = QHBoxLayout()
        contentRow.addWidget(self.controlsPanel)
        contentRow.addWidget(self.conversationPanel)
        self.mainLayout.addLayout(contentRow)

        # ⇨ déclenche la transcription quand le fichier est réellement prêt
        audio_service.recordingFinished.connect(self._onRecordingFinished)
        audio_service.recordingStoppedByLimit.connect(self.controlsPanel._handle_auto_stop)

        # Connexion du signal de transcription vers une méthode dans le thread UI
        self.transcriptionReady.connect(self._onTranscriptionDone)

        load_qss_for(self)
        self.applyUiState()

    def _addHeader(self) -> None:
        header = QHBoxLayout()

        title = QLabel(ParliaStrings.Home.TRANSCRIPTION_TITLE, self)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(title)

        header.addStretch()

        gearButton = QToolButton(self)
        gearButton.setIcon(qta.icon("fa5s.cog", color="#E5E5E5"))
        gearButton.setToolTip("Ouvrir les paramètres de transcription")
        gearButton.setFixedSize(32, 32)
        gearButton.clicked.connect(self.openTranscriptionSettings)
        header.addWidget(gearButton)

        self.mainLayout.addLayout(header)

    def openTranscriptionSettings(self) -> None:
        dlg = TranscriptionSettingsDialog(self)
        dlg.exec_()

    # --- Orchestration ---

    def applyUiState(self) -> None:
        pass

    @Slot(dict)
    def _onTranscriptionDone(self, result: dict[str, Any]) -> None:
        stateManager = AppStateManager()
        """Met à jour l'UI depuis le thread principal (appelé via Signal)."""
        if not result or "error" in result:
            self.conversationPanel.setMessageText("⚠️ Erreur lors de la transcription.")
            return
        text = result.get("text", "")
        self.conversationPanel.setMessageText(text)
        stateManager.markTranscriptionReady()

    # --- Lifecycle ---

    def closeEvent(self, event):
        try:
            ia_server_service.cleanup()
        except Exception as e:
            logger.error(f"[TranscriptionPanel] cleanup error: {e}")
        super().closeEvent(event)

    def _onRecordingStarted(self) -> None:
        logger.info("[TranscriptionPanel] _onRecordingStarted")
        audio_service.start_recording()
        audio_service.connect_timer(self.controlsPanel.updateTimerLabel)

    def _onRecordingStopped(self) -> None:
        # Arrêt uniquement ; la transcription sera lancée sur recordingFinished(path)
        logger.info("[TranscriptionPanel] _onRecordingStopped")
        audio_service.stop_recording()
        AppStateManager().requestStopRecordingAndProcess()

    def _onRecordingFinished(self, filePath: str) -> None:
        # Lance la transcription uniquement quand le fichier est prêt
        if not filePath:
            return

        # ⚠️ Le callback sera exécuté dans un thread → on émet un Signal
        def _callback(result: dict[str, Any]) -> None:
            self.transcriptionReady.emit(result)

        ia_server_service.whisper.transcribe_async(
            filePath,
            callback=_callback,
        )

    def _onCopyMessage(self) -> None:
        text = self.conversationPanel.getMessageText()
        QApplication.clipboard().setText(text)

    def _onCopyResponse(self) -> None:
        text = self.conversationPanel.getResponseText()
        QApplication.clipboard().setText(text)
