# controls_panel.py

from typing import Optional

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

from modules.parlia.i18n.parlia_strings import ParliaStrings
from modules.parlia.services.parlia_data import get_max_duration, set_max_duration


class ControlsPanel(QWidget):
    """UI gauche : contrôles d'enregistrement + actions (sans logique métier)."""

    # --- Signaux émis vers l'orchestrateur ---
    recordingStarted = Signal()
    recordingStopped = Signal()
    copyMessageRequested = Signal()
    copyResponseRequested = Signal()
    relayRequested = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.isRecording: bool = False

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
        """MAJ timer enregistrement."""
        minutes = int(seconds) // 60
        sec = int(seconds) % 60
        self.recordingTimerLabel.setText(f"{minutes:02}:{sec:02}")

    def updateTranscriptionTimer(self, seconds: float) -> None:
        """MAJ timer transcription."""
        minutes = int(seconds) // 60
        sec = int(seconds) % 60
        fraction = int((seconds - int(seconds)) * 100)
        self.transcriptionTimerLabel.setText(f"{minutes:02}:{sec:02}.{fraction:02}")

    # --- Slots / signaux ---

    @Slot()
    def toggleRecording(self) -> None:
        """Bascule UI start/stop et émet le signal correspondant."""
        if not self.isRecording:
            self._startRecordingUi()
            self.recordingStarted.emit()
        else:
            self._stopRecordingUi()
            self.recordingStopped.emit()

    def _startRecordingUi(self) -> None:
        self.isRecording = True
        self.recordButton.setText(ParliaStrings.Transcription.STOP)
        self.recordButton.setObjectName("stopButton")
        self.recordButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.recordButton.style().unpolish(self.recordButton)
        self.recordButton.style().polish(self.recordButton)

    def _stopRecordingUi(self) -> None:
        self.isRecording = False
        self.recordButton.setText(ParliaStrings.Transcription.RECORD)
        self.recordButton.setObjectName("recordButton")
        self.recordButton.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.recordButton.style().unpolish(self.recordButton)
        self.recordButton.style().polish(self.recordButton)

    @Slot()
    def _emitCopyMessage(self) -> None:
        self.copyMessageRequested.emit()

    @Slot()
    def _emitCopyResponse(self) -> None:
        self.copyResponseRequested.emit()

    @Slot()
    def _emitRelay(self) -> None:
        self.relayRequested.emit()

    # --- Helpers état UI ---

    def setRecordingEnabled(self, enabled: bool) -> None:
        """Active/désactive le bouton d'enregistrement."""
        self.recordButton.setEnabled(enabled)
