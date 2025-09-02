# src/modules/parlia/ui/transcription/transcription_panel.py
from __future__ import annotations

from typing import Any, Optional

import qtawesome as qta
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QCloseEvent
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
    """Orchestrator: ControlsPanel + ConversationPanel."""

    transcriptionReady = Signal(dict)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.mainLayout = QVBoxLayout(self)
        self._addHeader()

        self.controlsPanel = ControlsPanel(parent=self)
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

        audio_service.recordingFinished.connect(self._onRecordingFinished)
        audio_service.recordingStoppedByLimit.connect(self.controlsPanel._handle_auto_stop)

        # 🔴 Nouveau: écouter les partiels du streaming
        audio_service.partialTranscriptAvailable.connect(self._onPartialTranscript)

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

    # --- UI state ---

    def applyUiState(self) -> None:
        pass

    # --- Streaming partiels → append UI ---

    @Slot(str)
    def _onPartialTranscript(self, text: str) -> None:
        # append incremental text sans écraser
        current = self.conversationPanel.getMessageText()
        sep = "" if not current or current.endswith((" ", "\n")) else " "
        self.conversationPanel.setMessageText(f"{current}{sep}{text}")

    # --- Final transcription ---

    @Slot(dict)
    def _onTranscriptionDone(self, result: dict[str, Any]) -> None:
        stateManager = AppStateManager()
        if not result or "error" in result:
            self.conversationPanel.setMessageText("⚠️ Erreur lors de la transcription.")
            return
        text = result.get("text", "")
        self.conversationPanel.setMessageText(text)
        stateManager.markTranscriptionReady()

    # --- Lifecycle ---

    def closeEvent(self, event: QCloseEvent) -> None:
        try:
            ia_server_service.cleanup()
        except Exception as e:
            logger.error(f"[TranscriptionPanel] cleanup error: {e}")
        super().closeEvent(event)

    # --- Non-streaming flow (existant) ---

    def _onRecordingStarted(self) -> None:
        logger.info("[TranscriptionPanel] _onRecordingStarted")
        # Read selected mode from ControlsPanel
        mode = (
            self.controlsPanel.getSelectedMode()
            if hasattr(self.controlsPanel, "getSelectedMode")
            else (
                self.controlsPanel.selectedMode()
                if hasattr(self.controlsPanel, "selectedMode")
                else "classic"
            )
        )

        if mode == "streaming":
            audio_service.startStreamingRecording()
        else:
            audio_service.start_recording()

        audio_service.connect_timer(self.controlsPanel.updateTimerLabel)

    def _onRecordingStopped(self) -> None:
        logger.info("[TranscriptionPanel] _onRecordingStopped")
        # Read selected mode from ControlsPanel
        mode = (
            self.controlsPanel.getSelectedMode()
            if hasattr(self.controlsPanel, "getSelectedMode")
            else (
                self.controlsPanel.selectedMode()
                if hasattr(self.controlsPanel, "selectedMode")
                else "classic"
            )
        )

        if mode == "streaming":
            audio_service.stopStreamingRecording()
        else:
            audio_service.stop_recording()

        AppStateManager().requestStopRecordingAndProcess()

    def _onRecordingFinished(self, filePath: str) -> None:
        if not filePath:
            return

        def _callback(result: dict[str, Any]) -> None:
            self.transcriptionReady.emit(result)

        ia_server_service.whisper.transcribe_async(
            filePath,
            callback=_callback,
        )

    # --- Copy helpers ---

    def _onCopyMessage(self) -> None:
        text = self.conversationPanel.getMessageText()
        QApplication.clipboard().setText(text)

    def _onCopyResponse(self) -> None:
        text = self.conversationPanel.getResponseText()
        QApplication.clipboard().setText(text)
