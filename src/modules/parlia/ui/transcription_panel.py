# transcription_panel.py

from typing import Optional

import qtawesome as qta
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont, QTextCharFormat
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStyle,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from modules.parlia.i18n.parlia_strings import ParliaStrings
from modules.parlia.services.audioService import audio_service
from modules.parlia.services.parlia_data import get_max_duration, set_max_duration
from modules.parlia.services.whisper_service import whisper_service

# from modules.parlia.ui.dialogs.action_settings_dialog import ActionSettingsDialog
from modules.parlia.ui.dialogs.transcription_settings_dialog import (
    TranscriptionSettingsDialog,
)
from modules.parlia.utils.stylesheet_loader import load_qss_for
from src.core.logger_manager import get_logger

logger = get_logger("TranscriptionPanel")


class TranscriptionPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Création des layouts
        self.main_layout = QVBoxLayout()
        self._add_header()

        content_layout = QHBoxLayout()
        self.left_panel = self.create_left_side()
        self.right_panel = self.create_right_side()
        content_layout.addWidget(self.left_panel)
        content_layout.addWidget(self.right_panel)

        self.main_layout.addLayout(content_layout)
        self.setLayout(self.main_layout)
        load_qss_for(self)

        # État UI initial (simplifié, sans statut local)
        self.apply_ui_state()

    def _add_header(self) -> None:
        """
        Ajouter un en-tête avec un titre et un bouton engrenage.
        """
        header_layout = QHBoxLayout()

        # Titre "Transcription"
        title_label = QLabel(ParliaStrings.Home.TRANSCRIPTION_TITLE, self)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)

        # Ajouter un stretch pour pousser le bouton engrenage à droite
        header_layout.addStretch()

        # Bouton engrenage
        gear_button = QToolButton(self)
        gear_button.setIcon(qta.icon("fa5s.cog", color="#E5E5E5"))
        gear_button.setToolTip("Ouvrir les paramètres de transcription")
        gear_button.setFixedSize(32, 32)
        gear_button.clicked.connect(self.open_transcription_settings)
        header_layout.addWidget(gear_button)

        # Ajouter le layout à l'interface principale
        self.main_layout.addLayout(header_layout)

    def open_transcription_settings(self) -> None:
        """
        Ouvre la fenêtre TranscriptionSettingsDialog en modal.
        """
        transcription_settings_dialog = TranscriptionSettingsDialog(self)
        transcription_settings_dialog.exec_()

    def create_left_side(self) -> QWidget:
        """
        Create the left side of the panel with buttons, labels, etc.
        """
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        # (Statut local supprimé)

        # Section durées
        self.manage_times(left_layout)

        # Bouton d'enregistrement
        record_button = self.create_record_button()
        left_layout.addSpacing(10)
        left_layout.addWidget(record_button)

        left_widget.setLayout(left_layout)
        return left_widget

    def create_record_button(self) -> QPushButton:
        """
        Create and configure the record button with toggle behavior.
        """
        self.is_recording = False  # Initial recording state

        self.record_button = QPushButton(ParliaStrings.Transcription.RECORD)
        self.record_button.setObjectName("recordButton")
        self.record_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.record_button.setEnabled(True)  # plus de check parlia_state

        self.record_button.clicked.connect(self.toggle_recording)
        return self.record_button

    @Slot()
    def toggle_recording(self):
        """
        Toggle the recording state and update the button text/icon.
        """
        logger.info("[PANEL] toggle_recording() exécuté")

        if not self.is_recording:
            logger.info("Starting recording...")
            self.is_recording = True
            self.record_button.setText(ParliaStrings.Transcription.STOP)
            self.record_button.setObjectName("stopButton")
            self.record_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop)
            )
            self.record_button.style().unpolish(self.record_button)
            self.record_button.style().polish(self.record_button)
            audio_service.start_recording()
            audio_service.connect_timer(self.update_timer_label)
            logger.info("Recording started...")
        else:
            logger.info("Stopping recording...")
            self.is_recording = False
            self.record_button.setText(ParliaStrings.Transcription.RECORD)
            self.record_button.setObjectName("recordButton")
            self.record_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )
            self.record_button.style().unpolish(self.record_button)
            self.record_button.style().polish(self.record_button)
            audio_service.stop_recording()
            logger.info("Recording stopped...")

            # ⏳ Transcription asynchrone (sans parlia_state)
            whisper_service.transcribe_async(callback=self._on_transcription_done)
            whisper_service.connect_transcription_timer(self.update_transcription_timer)

    def manage_times(self, layout: QVBoxLayout) -> None:
        """
        Manage time-related elements in the layout.
        """
        # Add max duration section
        max_duration_layout = self.create_max_duration_section()
        layout.addLayout(max_duration_layout)

        # Add recording time section
        recording_time_layout = self.create_recording_time_section()
        layout.addLayout(recording_time_layout)

        # Add transcription time section
        transcription_time_layout = self.create_transcription_time_section()
        layout.addLayout(transcription_time_layout)

    def create_max_duration_section(self) -> QHBoxLayout:
        """
        Create the max duration section with a label and combobox.
        Load saved duration from UserDataManager and save changes to parlia.jsonData.
        """
        max_duration_label = QLabel(ParliaStrings.Transcription.MAX_DURATION)
        self.max_duration_combobox = QComboBox(self)

        self._populate_duration_options()
        self._load_saved_duration()

        # Save changes to UserDataManager on selection change
        self.max_duration_combobox.currentIndexChanged.connect(self.save_max_duration)

        max_duration_layout = QHBoxLayout()
        max_duration_layout.addWidget(max_duration_label)
        max_duration_layout.addWidget(self.max_duration_combobox)

        return max_duration_layout

    def _populate_duration_options(self) -> None:
        """
        Populate the combobox with predefined duration options.
        """
        self.duration_options = {
            0: ParliaStrings.Transcription.NO_DURATION,
            1: ParliaStrings.Transcription.DURATION_1_MIN,
            2: ParliaStrings.Transcription.DURATION_2_MIN,
            5: ParliaStrings.Transcription.DURATION_5_MIN,
            10: ParliaStrings.Transcription.DURATION_10_MIN,
            15: ParliaStrings.Transcription.DURATION_15_MIN,
        }

        for key, value in self.duration_options.items():
            self.max_duration_combobox.addItem(value, int(key))

    def _load_saved_duration(self) -> None:
        saved_duration_key = get_max_duration()
        logger.info(f"Loaded saved duration key: {saved_duration_key}")

        if saved_duration_key is not None and int(saved_duration_key) in self.duration_options:
            index = self.max_duration_combobox.findData(int(saved_duration_key))

            if index != -1:
                self.max_duration_combobox.setCurrentIndex(index)
        else:
            self.max_duration_combobox.setCurrentIndex(0)

        # Mise à jour de la persistance seulement
        current_key = self.max_duration_combobox.currentData()
        set_max_duration(current_key)

    def save_max_duration(self) -> None:
        """
        Save the selected max duration key to UserDataManager.
        """
        selected_key = self.max_duration_combobox.currentData()
        set_max_duration(selected_key)

    def create_recording_time_section(self) -> QHBoxLayout:
        """
        Create the recording time section with a label and timer.
        """
        recording_time_label = QLabel(ParliaStrings.Transcription.RECORDING_TIME)
        self.recording_timer_label = QLabel(ParliaStrings.Transcription.TIMER_DEFAULT)
        self.recording_timer_label.setProperty("class", "timerLabel")

        recording_time_layout = QHBoxLayout()
        recording_time_layout.addWidget(recording_time_label)
        recording_time_layout.addWidget(self.recording_timer_label)

        return recording_time_layout

    def update_timer_label(self, seconds: float) -> None:
        minutes = int(seconds) // 60
        sec = int(seconds) % 60
        self.recording_timer_label.setText(f"{minutes:02}:{sec:02}")

    def create_transcription_time_section(self) -> QHBoxLayout:
        transcription_time_label = QLabel(ParliaStrings.Transcription.TRANSCRIPTION_TIME)
        self.transcription_timer_label = QLabel(ParliaStrings.Transcription.TIMER_DEFAULT)
        self.transcription_timer_label.setProperty("class", "timerLabel")

        transcription_time_layout = QHBoxLayout()
        transcription_time_layout.addWidget(transcription_time_label)
        transcription_time_layout.addWidget(self.transcription_timer_label)

        return transcription_time_layout

    def update_transcription_timer(self, seconds: float) -> None:
        minutes = int(seconds) // 60
        sec = int(seconds) % 60
        fraction = int((seconds - int(seconds)) * 100)
        self.transcription_timer_label.setText(f"{minutes:02}:{sec:02}.{fraction:02}")

    def create_right_side(self) -> QWidget:
        """
        Create the right side of the panel with a QTextEdit for transcription text and a formatting toolbar.
        """
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        transcription_text = self.create_transcription_text()
        right_layout.addWidget(transcription_text)

        right_widget.setLayout(right_layout)
        return right_widget

    def create_formatting_toolbar(self) -> QHBoxLayout:
        """
        Create a formatting toolbar with buttons for bold, italic, emoji, and clear formatting.
        """
        toolbar_layout = QHBoxLayout()

        bold_button = QPushButton("B")
        bold_button.setToolTip("Apply bold formatting")
        bold_button.clicked.connect(self.apply_bold_formatting)
        toolbar_layout.addWidget(bold_button)

        italic_button = QPushButton("I")
        italic_button.setToolTip("Apply italic formatting")
        italic_button.clicked.connect(self.apply_italic_formatting)
        toolbar_layout.addWidget(italic_button)

        emoji_button = QPushButton("😊")
        emoji_button.setToolTip("Insert emoji")
        emoji_button.clicked.connect(self.insert_emoji)
        toolbar_layout.addWidget(emoji_button)

        clear_button = QPushButton("🧽")
        clear_button.setToolTip("Clear formatting")
        clear_button.clicked.connect(self.clear_formatting)
        toolbar_layout.addWidget(clear_button)

        return toolbar_layout

    def create_transcription_text(self) -> QTextEdit:
        """
        Create and configure a QTextEdit for transcription results.
        """
        transcription_text = QTextEdit()
        transcription_text.setPlaceholderText(ParliaStrings.Transcription.TRANSCRIBED_TEXT)
        transcription_text.setAcceptRichText(True)
        transcription_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        transcription_text.setFont(QFont("Courier New", 10))  # Monospace font
        transcription_text.setStyleSheet("padding: 10px;")
        transcription_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        transcription_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.transcription_text = transcription_text
        return transcription_text

    def _on_transcription_done(self, text: Optional[str]) -> None:
        """
        Callback appelé automatiquement à la fin de la transcription.
        Affiche le texte transcrit ou un message d’erreur.
        """
        if text is None:
            self.transcription_text.setPlainText("⚠️ Erreur lors de la transcription.")
        else:
            self.transcription_text.setPlainText(text)

        # Plus de gestion d'état local ici

    def apply_bold_formatting(self) -> None:
        cursor = self.transcription_text.textCursor()
        if cursor.hasSelection():
            format = QTextCharFormat()
            format.setFontWeight(QFont.Weight.Bold)
            cursor.mergeCharFormat(format)

    def apply_italic_formatting(self) -> None:
        cursor = self.transcription_text.textCursor()
        if cursor.hasSelection():
            format = QTextCharFormat()
            format.setFontItalic(True)
            cursor.mergeCharFormat(format)

    def insert_emoji(self) -> None:
        cursor = self.transcription_text.textCursor()
        cursor.insertText("😊")

    def clear_formatting(self) -> None:
        cursor = self.transcription_text.textCursor()
        if cursor.hasSelection():
            format = QTextCharFormat()
            format.setFontWeight(QFont.Weight.Normal)
            format.setFontItalic(False)
            cursor.mergeCharFormat(format)

    def get_transcription_text(self) -> str:
        """
        Retrieve the text from the transcription text field.
        """
        text = self.transcription_text.toPlainText()
        logger.info(f"Transcription text retrieved: {text}")
        return text

    def apply_ui_state(self) -> None:
        # Simplifié : pas de statut local, bouton actif par défaut
        if not hasattr(self, "record_button"):
            logger.warning("[WARN] apply_ui_state() appelé trop tôt")
            return
        self.record_button.setEnabled(True)

    def closeEvent(self, event):
        self.__deleted__ = True
        try:
            whisper_service.cleanup()
        except Exception as e:
            logger.error(f"[Panel] Erreur lors du cleanup : {e}")
        super().closeEvent(event)
