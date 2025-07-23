from typing import Optional

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont, QTextCharFormat
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStyle,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from modules.parlia.services.audioService import audio_service
from modules.parlia.services.parlia_data import get_max_duration, set_max_duration
from modules.parlia.services.parlia_state_manager import parlia_state
from modules.parlia.services.whisper_service import whisper_service
from modules.parlia.settings import ParliaSettings
from modules.parlia.utils.stylesheet_loader import load_qss_for


class TranscriptionPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.model_ready = True  # à remplacer si tu veux mettre une vraie logique
        # self.model_ready = whisper_service.is_ready()

        # Création des layouts
        main_layout = QHBoxLayout()
        self.left_panel = self.create_left_side()
        self.right_panel = self.create_right_side()
        main_layout.addWidget(self.left_panel)
        main_layout.addWidget(self.right_panel)
        self.setLayout(main_layout)
        load_qss_for(self)

        # ✅ Maintenant que tous les attributs sont là, on peut s’abonner en toute sécurité
        parlia_state.register_ui_component(self)
        self.apply_ui_state()

    def create_left_side(self):
        """
        Create the left side of the panel with buttons, labels, etc.
        """
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        # Add a status label
        status_layout = QHBoxLayout()
        static_status_label = QLabel(ParliaSettings.LABEL_STATUT)
        self.status_value_label = QLabel()

        self.status_value_label.setObjectName("statusLabel")
        status_layout.addWidget(static_status_label)
        status_layout.addWidget(self.status_value_label)
        left_layout.addLayout(status_layout)

        # Add a time management section
        self.manage_times(left_layout)

        # Add a record button
        record_button = self.create_record_button()
        left_layout.addSpacing(10)
        left_layout.addWidget(record_button)

        self.update_record_button_state()

        left_widget.setLayout(left_layout)
        return left_widget

    def create_record_button(self) -> QPushButton:
        """
        Create and configure the record button with toggle behavior.
        """
        self.is_recording = False  # Initial recording state

        self.record_button = QPushButton(ParliaSettings.LABEL_RECORD)
        self.record_button.setObjectName("recordButton")
        self.record_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        )
        self.record_button.setEnabled(
            parlia_state.is_ready_to_record()
        )  # Désactivé par défaut

        self.record_button.clicked.connect(self.toggle_recording)
        return self.record_button

    @Slot()
    def toggle_recording(self):
        """
        Toggle the recording state and update the button text/icon.
        """
        print("[PANEL] toggle_recording() exécuté")

        if not self.is_recording:
            print("Starting recording...")
            self.is_recording = True
            self.record_button.setText(ParliaSettings.LABEL_STOP)
            self.record_button.setObjectName("stopButton")
            self.record_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop)
            )
            self.record_button.style().unpolish(self.record_button)
            self.record_button.style().polish(self.record_button)
            audio_service.start_recording()
            audio_service.connect_timer(self.update_timer_label)
            print("Recording started...")
        else:
            print("Stopping recording...")
            self.is_recording = False
            self.record_button.setText(ParliaSettings.LABEL_RECORD)
            self.record_button.setObjectName("recordButton")
            self.record_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )
            self.record_button.style().unpolish(self.record_button)
            self.record_button.style().polish(self.record_button)
            audio_service.stop_recording()
            print("Recording stopped...")

            # ⏳ Transcription asynchrone
            parlia_state.set_transcribing(True)
            whisper_service.transcribe_async(callback=self._on_transcription_done)
            whisper_service.connect_transcription_timer(self.update_transcription_timer)

    def manage_times(self, layout: QVBoxLayout):
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

    def create_max_duration_section(self):
        """
        Create the max duration section with a label and combobox.
        Load saved duration from UserDataManager and save changes to parlia.jsonData.
        """
        max_duration_label = QLabel(ParliaSettings.LABEL_MAX_DURATION)
        self.max_duration_combobox = QComboBox()

        self._populate_duration_options()
        self._load_saved_duration()

        # Save changes to UserDataManager on selection change
        self.max_duration_combobox.currentIndexChanged.connect(self.save_max_duration)

        max_duration_layout = QHBoxLayout()
        max_duration_layout.addWidget(max_duration_label)
        max_duration_layout.addWidget(self.max_duration_combobox)

        return max_duration_layout

    def _populate_duration_options(self):
        """
        Populate the combobox with predefined duration options.
        """
        self.duration_options = {
            "0": ParliaSettings.LABEL_NO_DURATION,
            "1": ParliaSettings.LABEL_DURATION_1_MIN,
            "2": ParliaSettings.LABEL_DURATION_2_MIN,
            "5": ParliaSettings.LABEL_DURATION_5_MIN,
            "10": ParliaSettings.LABEL_DURATION_10_MIN,
            "15": ParliaSettings.LABEL_DURATION_15_MIN,
        }

        for key, value in self.duration_options.items():
            self.max_duration_combobox.addItem(value, key)

    def _load_saved_duration(self):
        saved_duration_key = get_max_duration()
        print(f"Loaded saved duration key: {saved_duration_key}")

        # DÉFÉRER le set_max_duration si les widgets ne sont pas encore prêts
        if saved_duration_key and saved_duration_key in self.duration_options:
            index = self.max_duration_combobox.findData(saved_duration_key)
            if index != -1:
                self.max_duration_combobox.setCurrentIndex(index)
        else:
            self.max_duration_combobox.setCurrentIndex(0)

    def save_max_duration(self):
        """
        Save the selected max duration key to UserDataManager.
        """
        selected_key = self.max_duration_combobox.currentData()
        set_max_duration(selected_key)
        if selected_key.isdigit():
            parlia_state.set_max_duration(int(selected_key))

    def create_recording_time_section(self):
        """
        Create the recording time section with a label and timer.
        """
        recording_time_label = QLabel(ParliaSettings.LABEL_RECORDING_TIME)
        self.recording_timer_label = QLabel(ParliaSettings.LABEL_TIMER_DEFAULT)
        self.recording_timer_label.setProperty("class", "timerLabel")

        recording_time_layout = QHBoxLayout()
        recording_time_layout.addWidget(recording_time_label)
        recording_time_layout.addWidget(self.recording_timer_label)

        return recording_time_layout

    def update_timer_label(self, seconds: float):
        minutes = int(seconds) // 60
        sec = int(seconds) % 60
        self.recording_timer_label.setText(f"{minutes:02}:{sec:02}")

    def create_transcription_time_section(self):
        transcription_time_label = QLabel(ParliaSettings.LABEL_TRANSCRIPTION_TIME)
        self.transcription_timer_label = QLabel(ParliaSettings.LABEL_TIMER_DEFAULT)
        self.transcription_timer_label.setProperty("class", "timerLabel")

        transcription_time_layout = QHBoxLayout()
        transcription_time_layout.addWidget(transcription_time_label)
        transcription_time_layout.addWidget(self.transcription_timer_label)

        return transcription_time_layout

    def update_transcription_timer(self, seconds: float):
        minutes = int(seconds) // 60
        sec = int(seconds) % 60
        fraction = int(
            (seconds - int(seconds)) * 100
        )  # ou remplacer par * 10 pour avec des dixièmes
        self.transcription_timer_label.setText(f"{minutes:02}:{sec:02}.{fraction:02}")

    def create_right_side(self):
        """
        Create the right side of the panel with a QTextEdit for transcription text and a formatting toolbar.
        """
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        transcription_text = self.create_transcription_text()
        right_layout.addWidget(transcription_text)

        right_widget.setLayout(right_layout)
        return right_widget

    def create_formatting_toolbar(self):
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

    def create_transcription_text(self):
        """
        Create and configure a QTextEdit for transcription results.
        """
        transcription_text = QTextEdit()
        transcription_text.setPlaceholderText(ParliaSettings.LABEL_TRANSCRIBED_TEXT)
        transcription_text.setAcceptRichText(True)
        transcription_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        transcription_text.setFont(QFont("Courier New", 10))  # Monospace font
        transcription_text.setStyleSheet("padding: 10px;")
        transcription_text.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        transcription_text.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.transcription_text = transcription_text
        return transcription_text

    def _on_transcription_done(self, text: Optional[str]):
        """
        Callback appelé automatiquement à la fin de la transcription.
        Affiche le texte transcrit ou un message d’erreur.
        """
        if text is None:
            self.transcription_text.setPlainText("⚠️ Erreur lors de la transcription.")
        else:
            self.transcription_text.setPlainText(text)

        # Réactiver les boutons, réinitialiser l’état
        parlia_state.set_transcribing(False)
        self.update_record_button_state()

    def apply_bold_formatting(self):
        cursor = self.transcription_text.textCursor()
        if cursor.hasSelection():
            format = QTextCharFormat()
            format.setFontWeight(QFont.Weight.Bold)
            cursor.mergeCharFormat(format)

    def apply_italic_formatting(self):
        cursor = self.transcription_text.textCursor()
        if cursor.hasSelection():
            format = QTextCharFormat()
            format.setFontItalic(True)
            cursor.mergeCharFormat(format)

    def insert_emoji(self):
        cursor = self.transcription_text.textCursor()
        cursor.insertText("😊")

    def clear_formatting(self):
        cursor = self.transcription_text.textCursor()
        if cursor.hasSelection():
            format = QTextCharFormat()
            format.setFontWeight(QFont.Weight.Normal)
            format.setFontItalic(False)
            cursor.mergeCharFormat(format)

    def get_transcription_text(self):
        """
        Retrieve the text from the transcription text field.
        """
        text = self.transcription_text.toPlainText()
        print(f"Transcription text retrieved: {text}")
        return text

    def update_record_button_state(self):
        self.record_button.setEnabled(parlia_state.is_ready_to_record())

    def closeEvent(self, event):
        self.__deleted__ = True
        try:
            parlia_state.unregister_ui_component(self)
            whisper_service.cleanup()
        except Exception as e:
            print(f"[Panel] Erreur lors du désabonnement : {e}")
        super().closeEvent(event)

    def update_status_label(self):
        text, status_type = parlia_state.get_status_info()
        self.status_value_label.setText(text)

        # Appliquer dynamiquement la classe CSS
        self.status_value_label.setObjectName(f"statusLabel_{status_type}")
        self.status_value_label.style().unpolish(self.status_value_label)
        self.status_value_label.style().polish(self.status_value_label)

    def apply_ui_state(self):
        if not hasattr(self, "record_button"):
            print("[WARN] apply_ui_state() appelé trop tôt")
            return
        self.record_button.setEnabled(parlia_state.is_ready_to_record())
        self.max_duration_combobox.setEnabled(not parlia_state.is_ui_locked())
        self.update_status_label()
