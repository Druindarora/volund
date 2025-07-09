from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCharFormat
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class TranscriptionPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create the main horizontal layout with two panels (left and right)
        main_layout = QHBoxLayout()
        self.left_panel = self.create_left_side()
        self.right_panel = self.create_right_side()

        main_layout.addWidget(self.left_panel)
        main_layout.addWidget(self.right_panel)
        self.setLayout(main_layout)

    def create_left_side(self):
        """
        Create the left side of the panel with buttons, labels, etc.
        """
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        # Add a status label
        status_label = QLabel("Statut : Prêt")
        left_layout.addWidget(status_label)

        # Add a time management section
        self.manage_times(left_layout)

        # Add a record button
        record_button = self.create_save_button()
        left_layout.addWidget(record_button)

        left_widget.setLayout(left_layout)
        return left_widget

    def create_save_button(self) -> QPushButton:
        """
        Create and configure the save button.
        """
        button = QPushButton("Enregistrer")
        # Configure button behavior here (e.g., connect signals)
        return button

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
        """
        max_duration_label = QLabel("Durée max :")
        max_duration_combobox = QComboBox()
        max_duration_combobox.addItems(
            [
                "Aucun temps",
                "1 minute",
                "2 minutes",
                "5 minutes",
                "10 minutes",
                "15 minutes",
            ]
        )

        max_duration_layout = QHBoxLayout()
        max_duration_layout.addWidget(max_duration_label)
        max_duration_layout.addWidget(max_duration_combobox)

        return max_duration_layout

    def create_recording_time_section(self):
        """
        Create the recording time section with a label and timer.
        """
        recording_time_label = QLabel("Temps d'enregistrement :")
        recording_timer = QLabel("00:00")

        recording_time_layout = QHBoxLayout()
        recording_time_layout.addWidget(recording_time_label)
        recording_time_layout.addWidget(recording_timer)

        return recording_time_layout

    def create_transcription_time_section(self):
        """
        Create the transcription time section with a label and timer.
        """
        transcription_time_label = QLabel("Temps de transcription :")
        transcription_timer = QLabel("00:00")

        transcription_time_layout = QHBoxLayout()
        transcription_time_layout.addWidget(transcription_time_label)
        transcription_time_layout.addWidget(transcription_timer)

        return transcription_time_layout

    def create_right_side(self):
        """
        Create the right side of the panel with a QTextEdit for transcription text and a formatting toolbar.
        """
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        # Add formatting toolbar
        # toolbar_layout = self.create_formatting_toolbar()
        # right_layout.addLayout(toolbar_layout)

        # Add QTextEdit for transcription results
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
        transcription_text.setPlaceholderText("Texte transcrit...")
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

    # Define formatting functions

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
