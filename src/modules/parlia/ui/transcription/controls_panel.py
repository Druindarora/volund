from typing import Any, Optional

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,  # ⬅️ NEW
    QStyle,
    QVBoxLayout,
    QWidget,
)

from modules.parlia.core.app_state_manager import AppStateManager, TranscriptionState
from modules.parlia.i18n.parlia_strings import ParliaStrings
from modules.parlia.services.parlia_data import (
    get_max_duration,
    get_transcription_mode,
    set_max_duration,
    set_transcription_mode,
)


class ControlsPanel(QWidget):
    """UI gauche : contrôles d'enregistrement (sans logique audio)."""

    # --- Signaux émis vers l'orchestrateur ---
    recordingStarted = Signal()
    recordingStopped = Signal()
    copyMessageRequested = Signal()
    copyResponseRequested = Signal()
    relayRequested = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.isRecording: bool = False
        self._capsCanRecord: bool = False
        self.stateManager = AppStateManager()
        self._mode: str = "classic"

        # Ne pas s'étirer en largeur : laisse la place au pane de droite
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)

        self.rootLayout = QVBoxLayout(self)
        self.rootLayout.setSpacing(20)
        # ⬇️ "padding-bottom" de 10px pour remonter l'ensemble par rapport au bord bas
        self.rootLayout.setContentsMargins(0, 0, 0, 30)

        self.rootLayout.addStretch(7)

        # Ligne 1 : Durée max
        self.rootLayout.addLayout(self._createMaxDurationSection())

        # Ligne 2 : Mode (Classique / Streaming)
        self.rootLayout.addLayout(self._createModeSection())
        self._loadSavedMode()

        # Stretch AVANT les timers pour pousser *timers + bouton* en bas ensemble
        self.rootLayout.addStretch(1)

        # Ligne 3 : Timers (enregistrement puis transcription, empilés verticalement)
        self.rootLayout.addLayout(self._createTimersSection())

        # Ligne 4 : Bouton Record (collé aux timers, petit espace)
        self.recordButton = QPushButton(ParliaStrings.Transcription.RECORD, self)
        self.recordButton.setObjectName("recordButton")
        self.recordButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.recordButton.setEnabled(True)
        self.recordButton.clicked.connect(self.toggleRecording)
        self.rootLayout.addSpacing(6)  # petit écart juste au-dessus du bouton
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
        self.stateManager.limitExceeded.connect(self._onLimitExceeded)

        # Snapshot initial
        self._applyInitialSnapshot()

    # --- Sections UI ---

    def _createMaxDurationSection(self) -> QHBoxLayout:
        label = QLabel(ParliaStrings.Transcription.MAX_DURATION, self)
        self.maxDurationComboBox = QComboBox(self)
        self._populateDurationOptions()
        self._loadSavedDuration()
        self.maxDurationComboBox.currentIndexChanged.connect(self._onDurationChanged)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(20)
        row.addWidget(label)
        row.addWidget(self.maxDurationComboBox)
        row.addStretch(1)
        return row

    def _createModeSection(self) -> QHBoxLayout:
        label = QLabel("Mode:", self)
        self.modeComboBox = QComboBox(self)
        self.modeComboBox.addItem("Classique", "classic")
        self.modeComboBox.addItem("Streaming", "streaming")

        # ⬅️ NEW: branchement du changement de mode
        self.modeComboBox.currentIndexChanged.connect(self._onModeChanged)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(20)
        row.addWidget(label)
        row.addWidget(self.modeComboBox)
        row.addStretch(1)
        return row

    def _createTimersSection(self) -> QVBoxLayout:
        """Two lines: recording timer on first line, transcription timer on second."""
        # Recording line
        recLabel = QLabel(ParliaStrings.Transcription.RECORDING_TIME, self)
        self.recordingTimerLabel = QLabel(ParliaStrings.Transcription.TIMER_DEFAULT, self)
        self.recordingTimerLabel.setProperty("class", "timerLabel")
        recRow = QHBoxLayout()
        recRow.setContentsMargins(0, 0, 0, 0)
        recRow.setSpacing(20)
        recRow.addWidget(recLabel)
        recRow.addWidget(self.recordingTimerLabel)
        recRow.addStretch(1)

        # Transcription line
        trLabel = QLabel(ParliaStrings.Transcription.TRANSCRIPTION_TIME, self)
        self.transcriptionTimerLabel = QLabel(ParliaStrings.Transcription.TIMER_DEFAULT, self)
        self.transcriptionTimerLabel.setProperty("class", "timerLabel")
        trRow = QHBoxLayout()
        trRow.setContentsMargins(0, 0, 0, 0)
        trRow.setSpacing(20)
        trRow.addWidget(trLabel)
        trRow.addWidget(self.transcriptionTimerLabel)
        trRow.addStretch(1)

        # Stack both lines vertically
        col = QVBoxLayout()
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(20)  # ⬅️ un chouia plus d'espace entre les deux lignes
        col.addLayout(recRow)
        col.addLayout(trRow)
        return col

    # --- Durée max / Mode / Timers (fonctions identiques à ta version) ---
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
        currentKey = self.maxDurationComboBox.currentData()
        set_max_duration(currentKey)

    def saveMaxDuration(self) -> None:
        selectedKey = self.maxDurationComboBox.currentData()
        set_max_duration(selectedKey)

    def _selectedMaxDuration(self) -> int:
        try:
            return int(self.maxDurationComboBox.currentData())
        except Exception:
            return 0

    def _selectedMode(self) -> str:
        data = self.modeComboBox.currentData()
        return str(data) if isinstance(data, (str, int)) else "classic"

    def selectedMode(self) -> str:
        return self._selectedMode()

    def updateTimerLabel(self, seconds: float) -> None:
        minutes = int(seconds) // 60
        sec = int(seconds) % 60
        self.recordingTimerLabel.setText(f"{minutes:02}:{sec:02}")

    def resetRecordingTimerLabel(self) -> None:
        self.recordingTimerLabel.setText(ParliaStrings.Transcription.TIMER_DEFAULT)
        self.recordingTimerLabel.setStyleSheet("")

    def updateTranscriptionTimer(self, seconds: float) -> None:
        minutes = int(seconds) // 60
        sec = int(seconds) % 60
        fraction = int((seconds - int(seconds)) * 100)
        self.transcriptionTimerLabel.setText(f"{minutes:02}:{sec:02}.{fraction:02}")

    def resetTranscriptionTimerLabel(self) -> None:
        self.transcriptionTimerLabel.setText(ParliaStrings.Transcription.TIMER_DEFAULT)

        # ⬅️ NEW: charge la valeur persistée et positionne la combo

    def _loadSavedMode(self) -> None:
        try:
            stored = get_transcription_mode()  # "classic" | "streaming" | None
        except Exception:
            stored = None
        if stored not in ("classic", "streaming"):
            stored = "classic"
        idx = self.modeComboBox.findData(stored)
        if idx != -1:
            self.modeComboBox.blockSignals(True)
            self.modeComboBox.setCurrentIndex(idx)
            self.modeComboBox.blockSignals(False)
        self._mode = stored

        # ⬅️ NEW: persiste et met à jour le cache quand l'utilisateur change

    @Slot()
    def _onModeChanged(self) -> None:
        value = self.getSelectedMode()
        self._mode = value
        try:
            set_transcription_mode(value)
        except Exception:
            pass

        # ⬅️ NEW: getter public demandé

    def getSelectedMode(self) -> str:
        data = self.modeComboBox.currentData()
        return str(data) if isinstance(data, (str, int)) else "classic"

    # def selectedMode(self) -> str:
    #     return self.getSelectedMode()

    # --- Slots / signaux / état (inchangés) ---
    @Slot()
    def toggleRecording(self) -> None:
        current = self.stateManager.currentState()
        if current == TranscriptionState.RECORDING or self.isRecording:
            modeValue = self.getSelectedMode()
            if modeValue == "streaming":
                # En streaming : envoyer "end" via le WebSocket, ne pas passer par PROCESSING, revenir immédiatement à l'UI idle
                try:
                    self.stateManager.requestStopStreaming()
                except Exception:
                    pass
                self._idleUi()
                self.setMaxDurationEnabled(True)
                self.recordingStopped.emit()
                return
            # Mode classique : comportement existant
            _accepted = self.stateManager.requestStopRecordingAndProcess()
            self.recordingStopped.emit()
            return

        if current in (TranscriptionState.IDLE, TranscriptionState.READY, TranscriptionState.ERROR):
            if self._selectedMaxDuration() <= 0:
                self.recordButton.setToolTip("Sélectionnez une durée d'enregistrement > 0 min.")
                try:
                    self.stateManager.actionRejected.emit(
                        "no_duration", "Durée d'enregistrement requise."
                    )
                except Exception:
                    pass
                return
            accepted = self.stateManager.requestStartRecording()
            if accepted:
                self.recordingStarted.emit()
            return

    def setRecordingEnabled(self, enabled: bool) -> None:
        self.recordButton.setEnabled(enabled)

    def setMaxDurationEnabled(self, enabled: bool) -> None:
        self.maxDurationComboBox.setEnabled(enabled)
        self.modeComboBox.setEnabled(enabled)

    def _processingText(self) -> str:
        return getattr(ParliaStrings.Transcription, "PROCESSING", "…")

    def _startRecordingUi(self) -> None:
        self.isRecording = True
        self.recordButton.setText(ParliaStrings.Transcription.STOP)
        self.recordButton.setObjectName("stopButton")
        self.recordButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.recordButton.setEnabled(True)
        self.recordButton.style().unpolish(self.recordButton)
        self.recordButton.style().polish(self.recordButton)

    def _processingUi(self) -> None:
        self.isRecording = False
        self.recordButton.setText(self._processingText())
        self.recordButton.setObjectName("processingButton")
        self.recordButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.recordButton.setEnabled(False)
        self.recordButton.style().unpolish(self.recordButton)
        self.recordButton.style().polish(self.recordButton)

    def _idleUi(self) -> None:
        self.isRecording = False
        self.recordButton.setText(ParliaStrings.Transcription.RECORD)
        self.recordButton.setObjectName("recordButton")
        self.recordButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.recordButton.style().unpolish(self.recordButton)
        self.recordButton.style().polish(self.recordButton)

    def _applyInitialSnapshot(self) -> None:
        state = self.stateManager.currentState()
        self._onStateChanged(state.value)
        busy = state in (TranscriptionState.RECORDING, TranscriptionState.PROCESSING)
        self.setMaxDurationEnabled(not busy)
        canRecord = self.stateManager.isWhisperReady() and not busy
        self._capsCanRecord = bool(canRecord)
        self._applyRecordingEnabledGate()
        self.resetRecordingTimerLabel()
        self.resetTranscriptionTimerLabel()

    def _applyRecordingEnabledGate(self) -> None:
        state = self.stateManager.currentState()
        if state == TranscriptionState.RECORDING:
            self.setRecordingEnabled(True)
            return
        if state == TranscriptionState.PROCESSING:
            self.setRecordingEnabled(False)
            return
        enabled = self._capsCanRecord and (self._selectedMaxDuration() > 0)
        self.setRecordingEnabled(enabled)
        if not enabled and self._selectedMaxDuration() <= 0:
            self.recordButton.setToolTip("Sélectionnez une durée d'enregistrement > 0 min.")
        else:
            self.recordButton.setToolTip("")

    @Slot(str)
    def _onStateChanged(self, stateValue: str) -> None:
        state = TranscriptionState(stateValue)
        if state == TranscriptionState.RECORDING:
            self._startRecordingUi()
            self.setMaxDurationEnabled(False)
        elif state == TranscriptionState.PROCESSING:
            self._processingUi()
            self.setMaxDurationEnabled(False)
        elif state in (TranscriptionState.READY, TranscriptionState.ERROR, TranscriptionState.IDLE):
            self._idleUi()
            self._applyRecordingEnabledGate()

    @Slot(dict)
    def _onCapabilities(self, caps: dict[str, Any]) -> None:
        self._capsCanRecord = bool(caps.get("canRecord", False))
        self._applyRecordingEnabledGate()

    @Slot(bool)
    def _onBusyChanged(self, busy: bool) -> None:
        self.setMaxDurationEnabled(not busy)
        self._applyRecordingEnabledGate()

    @Slot(str, str)
    def _onActionRejected(self, _reasonCode: str, message: str) -> None:
        self.recordButton.setToolTip(message)

    @Slot()
    def _handle_auto_stop(self) -> None:
        self.recordingStopped.emit()
        self.stateManager.requestStopRecordingAndProcess()

    @Slot()
    def _onDurationChanged(self) -> None:
        self.saveMaxDuration()
        self._applyRecordingEnabledGate()

    @Slot()
    def _onLimitExceeded(self) -> None:
        """Passe le timer d'enregistrement en rouge quand la limite est dépassée (mode streaming)."""
        self.recordingTimerLabel.setStyleSheet("color: #d9534f; font-weight: bold;")
