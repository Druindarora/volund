from typing import Any, Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStyle,
    QVBoxLayout,
    QWidget,
)

from modules.parlia.core.app_state_manager import AppStateManager, TranscriptionState
from modules.parlia.i18n.parlia_strings import ParliaStrings
from modules.parlia.services.parlia_data import get_max_duration, set_max_duration


class ControlsPanel(QWidget):
    """UI gauche : contrôles d'enregistrement (sans logique métier audio).

    Intègre AppStateManager pour :
      - verrouiller l'UI en fonction de l'état global (recording / processing / busy),
      - (dés)activer le bouton Record selon la disponibilité de Whisper,
      - suivre les timers d'enregistrement et de traitement client (Stop→texte),
      - empêcher toute modification de la durée max pendant rec/processing.

    L'orchestrateur applicatif doit se connecter aux signaux :
      - recordingStarted → démarrer la capture locale audio
      - recordingStopped → arrêter la capture et lancer l'upload/transcription
    et appeler ensuite côté AppStateManager :
      - markTranscriptionReady() OU markTranscriptionError()
      - éventuellement resetToIdle() après affichage.
    """

    # --- Signaux émis vers l'orchestrateur ---
    recordingStarted = Signal()
    recordingStopped = Signal()
    copyMessageRequested = Signal()
    copyResponseRequested = Signal()
    relayRequested = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.isRecording: bool = False  # état visuel local (synchro sur AppStateManager)

        # AppStateManager (singleton) et branchements signaux
        self.stateManager = AppStateManager()

        self.rootLayout = QVBoxLayout(self)

        # Section durées / timers
        self.rootLayout.addLayout(self._createMaxDurationSection())
        self.rootLayout.addLayout(self._createRecordingTimeSection())
        self.rootLayout.addLayout(self._createTranscriptionTimeSection())

        # Bouton start/stop
        self.recordButton = QPushButton(ParliaStrings.Transcription.RECORD, self)
        self.recordButton.setObjectName("recordButton")
        self.recordButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.recordButton.setEnabled(True)
        self.recordButton.clicked.connect(self.toggleRecording)
        self.rootLayout.addSpacing(10)
        self.rootLayout.addWidget(self.recordButton)

        # Connexions AppStateManager → UI
        self.stateManager.stateChanged.connect(self._onStateChanged)
        self.stateManager.capabilitiesUpdated.connect(self._onCapabilities)
        self.stateManager.busyChanged.connect(self._onBusyChanged)
        self.stateManager.recordingTimerTick.connect(self.updateTimerLabel)
        self.stateManager.processingTimerTick.connect(self.updateTranscriptionTimer)
        self.stateManager.recordingTimerReset.connect(self.resetRecordingTimerLabel)
        self.stateManager.processingTimerReset.connect(self.resetTranscriptionTimerLabel)
        self.stateManager.actionRejected.connect(self._onActionRejected)

        # Appliquer un snapshot initial (au cas où les signaux init ont été émis avant les connexions)
        self._applyInitialSnapshot()

    # --- Max duration ---

    def _createMaxDurationSection(self) -> QHBoxLayout:
        label = QLabel(ParliaStrings.Transcription.MAX_DURATION, self)
        self.maxDurationComboBox = QComboBox(self)

        self._populateDurationOptions()
        self._loadSavedDuration()
        self.maxDurationComboBox.currentIndexChanged.connect(self.saveMaxDuration)

        row = QHBoxLayout()
        row.addWidget(label)
        row.addWidget(self.maxDurationComboBox)
        return row

    def _populateDurationOptions(self) -> None:
        self.durationOptions: dict[int, str] = {
            0: ParliaStrings.Transcription.NO_DURATION,
            1: ParliaStrings.Transcription.DURATION_1_MIN,
            2: ParliaStrings.Transcription.DURATION_2_MIN,
            5: ParliaStrings.Transcription.DURATION_5_MIN,
            10: ParliaStrings.Transcription.DURATION_10_MIN,
            15: ParliaStrings.Transcription.DURATION_15_MIN,
        }
        for key, label in self.durationOptions.items():
            self.maxDurationComboBox.addItem(label, int(key))

    def _loadSavedDuration(self) -> None:
        savedKey = get_max_duration()
        if savedKey is not None and int(savedKey) in self.durationOptions:
            idx = self.maxDurationComboBox.findData(int(savedKey))
            if idx != -1:
                self.maxDurationComboBox.setCurrentIndex(idx)
        else:
            self.maxDurationComboBox.setCurrentIndex(0)
        # persistance simple
        currentKey = self.maxDurationComboBox.currentData()
        set_max_duration(currentKey)

    def saveMaxDuration(self) -> None:
        """Enregistre la durée max sélectionnée (persistance utilisateur)."""
        selectedKey = self.maxDurationComboBox.currentData()
        set_max_duration(selectedKey)

    # --- Timers ---

    def _createRecordingTimeSection(self) -> QHBoxLayout:
        label = QLabel(ParliaStrings.Transcription.RECORDING_TIME, self)
        self.recordingTimerLabel = QLabel(ParliaStrings.Transcription.TIMER_DEFAULT, self)
        self.recordingTimerLabel.setProperty("class", "timerLabel")
        row = QHBoxLayout()
        row.addWidget(label)
        row.addWidget(self.recordingTimerLabel)
        return row

    def _createTranscriptionTimeSection(self) -> QHBoxLayout:
        label = QLabel(ParliaStrings.Transcription.TRANSCRIPTION_TIME, self)
        self.transcriptionTimerLabel = QLabel(ParliaStrings.Transcription.TIMER_DEFAULT, self)
        self.transcriptionTimerLabel.setProperty("class", "timerLabel")
        row = QHBoxLayout()
        row.addWidget(label)
        row.addWidget(self.transcriptionTimerLabel)
        return row

    def updateTimerLabel(self, seconds: float) -> None:
        """MAJ timer enregistrement (mm:ss)."""
        minutes = int(seconds) // 60
        sec = int(seconds) % 60
        self.recordingTimerLabel.setText(f"{minutes:02}:{sec:02}")

    def resetRecordingTimerLabel(self) -> None:
        """Réinitialise le timer d'enregistrement (00:00)."""
        self.recordingTimerLabel.setText(ParliaStrings.Transcription.TIMER_DEFAULT)

    def updateTranscriptionTimer(self, seconds: float) -> None:
        """MAJ timer transcription (mm:ss.cc)."""
        minutes = int(seconds) // 60
        sec = int(seconds) % 60
        fraction = int((seconds - int(seconds)) * 100)
        self.transcriptionTimerLabel.setText(f"{minutes:02}:{sec:02}.{fraction:02}")

    def resetTranscriptionTimerLabel(self) -> None:
        """Réinitialise le timer de transcription (00:00.00)."""
        self.transcriptionTimerLabel.setText(ParliaStrings.Transcription.TIMER_DEFAULT)

    # --- Slots / signaux ---

    @Slot()
    def toggleRecording(self) -> None:
        """Demande de bascule start/stop via AppStateManager + émissions orchestrateur.

        - Start: on demande au StateManager; si accepté → on émet recordingStarted.
        - Stop:  on demande au StateManager; si accepté → on émet recordingStopped.
        """
        current = self.stateManager.currentState()
        if current in (TranscriptionState.IDLE, TranscriptionState.READY, TranscriptionState.ERROR):
            accepted = self.stateManager.requestStartRecording()
            if accepted:
                # L'orchestrateur démarre la capture audio locale
                self.recordingStarted.emit()
        elif current == TranscriptionState.RECORDING:
            accepted = self.stateManager.requestStopRecordingAndProcess()
            if accepted:
                # L'orchestrateur arrête la capture et lance upload/transcription
                self.recordingStopped.emit()
        else:
            # En PROCESSING → bouton normalement désactivé, on ignore.
            pass

    # --- Helpers état UI ---

    def setRecordingEnabled(self, enabled: bool) -> None:
        """Active/désactive le bouton d'enregistrement."""
        self.recordButton.setEnabled(enabled)

    def setMaxDurationEnabled(self, enabled: bool) -> None:
        """Active/désactive la combo de durée max."""
        self.maxDurationComboBox.setEnabled(enabled)

    def _processingText(self) -> str:
        """Libellé pour l'état processing (fallback si non traduit)."""
        return getattr(ParliaStrings.Transcription, "PROCESSING", "…")

    def _startRecordingUi(self) -> None:
        """UI pour état RECORDING."""
        self.isRecording = True
        self.recordButton.setText(ParliaStrings.Transcription.STOP)
        self.recordButton.setObjectName("stopButton")
        self.recordButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.recordButton.style().unpolish(self.recordButton)
        self.recordButton.style().polish(self.recordButton)

    def _processingUi(self) -> None:
        """UI pour état PROCESSING (bouton grisé et libellé adapté)."""
        self.isRecording = False
        self.recordButton.setText(self._processingText())
        self.recordButton.setObjectName("processingButton")
        self.recordButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.recordButton.setEnabled(False)
        self.recordButton.style().unpolish(self.recordButton)
        self.recordButton.style().polish(self.recordButton)

    def _idleUi(self) -> None:
        """UI pour états IDLE/READY/ERROR (retour au bouton Record)."""
        self.isRecording = False
        self.recordButton.setText(ParliaStrings.Transcription.RECORD)
        self.recordButton.setObjectName("recordButton")
        self.recordButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        # enabled sera fixé par capabilitiesUpdated
        self.recordButton.style().unpolish(self.recordButton)
        self.recordButton.style().polish(self.recordButton)

    # --- Réactions aux signaux AppStateManager ---

    def _applyInitialSnapshot(self) -> None:
        """Applique un snapshot initial basé sur l'état courant du StateManager."""
        state = self.stateManager.currentState()
        self._onStateChanged(state.value)
        busy = state in (TranscriptionState.RECORDING, TranscriptionState.PROCESSING)
        self.setMaxDurationEnabled(not busy)
        canRecord = self.stateManager.isWhisperReady() and not busy
        self.setRecordingEnabled(canRecord)
        # Timers → reset affichage initial
        self.resetRecordingTimerLabel()
        self.resetTranscriptionTimerLabel()

    @Slot(str)
    def _onStateChanged(self, stateValue: str) -> None:
        """Met à jour l'UI en fonction de l'état global de transcription."""
        state = TranscriptionState(stateValue)
        if state == TranscriptionState.RECORDING:
            self._startRecordingUi()
            self.setMaxDurationEnabled(False)
        elif state == TranscriptionState.PROCESSING:
            self._processingUi()
            self.setMaxDurationEnabled(False)
        elif state in (TranscriptionState.READY, TranscriptionState.ERROR, TranscriptionState.IDLE):
            self._idleUi()
            # L'activation du bouton est recalculée via capabilitiesUpdated

    @Slot(dict)
    def _onCapabilities(self, caps: dict[str, Any]) -> None:
        """Applique les capacités calculées (canRecord/canUseActions/busy)."""
        self.setRecordingEnabled(bool(caps.get("canRecord", False)))
        # canUseActions géré par l'ActionsPanel ; ici on s'occupe surtout de Record

    @Slot(bool)
    def _onBusyChanged(self, busy: bool) -> None:
        """(Dés)active les contrôles qui ne doivent pas changer en cours d'opération."""
        self.setMaxDurationEnabled(not busy)
        if busy:
            # Par cohérence, le bouton Record est géré par capabilities, mais si busy True, on force disabled
            self.setRecordingEnabled(False)

    @Slot(str, str)
    def _onActionRejected(self, reasonCode: str, message: str) -> None:
        """Feedback minimal en cas de refus (tooltip)."""
        self.recordButton.setToolTip(message)
        # Optionnel: logger/afficher un toast si nécessaire
