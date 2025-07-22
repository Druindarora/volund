from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from modules.parlia.config import config
from modules.parlia.services.action_service import copy_chatrelay_text, copy_text
from modules.parlia.services.chatgptService import (
    add_files_to_text_area,
    send_text_to_chatgpt,
)
from modules.parlia.services.vsCodeService import (
    analyze_code_to_vscode,
    explain_code_to_vscode,
    focus_and_paste_in_vscode,
    focus_vscode_and_refacto,
    focus_vscode_qt,
)
from modules.parlia.settings import ParliaSettings
from modules.parlia.ui.transcription_panel import TranscriptionPanel


class ActionPanel(QWidget):
    def __init__(self, transcription_panel: TranscriptionPanel, parent=None):
        super().__init__(parent)
        self.transcription_panel = transcription_panel

        # Create the main vertical layout for the action panel
        main_layout = QVBoxLayout()

        # Add status label at the top
        self.status_label = QLabel(ParliaSettings.LABEL_READY)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

        # First row: "Copier vers ChatRelay" and "Copier le texte"
        row1 = self.create_copy_row()
        main_layout.addLayout(row1)

        # Second row: "Ajouter des fichiers à la requête"
        row2 = self.create_file_row()
        main_layout.addLayout(row2)

        # Third row: "Focus vers ChatGPT" and "Focus vers VS Code"
        row3 = self.create_focus_row()
        main_layout.addLayout(row3)

        self.setLayout(main_layout)

    def create_copy_row(self):
        """
        Create first row with two buttons:
        - "Copier vers ChatRelay"
        - "Copier le texte"
        """
        layout = QHBoxLayout()
        layout.addWidget(self.create_chatrelay_button())
        layout.addWidget(self.create_copy_text_button())
        return layout

    def create_chatrelay_button(self):
        """
        Create the "Copier [ChatRelay]" button.
        """
        button = QPushButton(ParliaSettings.LABEL_CHATRELAY)
        button.clicked.connect(copy_chatrelay_text)
        return button

    def create_copy_text_button(self):
        """
        Create the "Copier le texte" button.
        """
        button = QPushButton(ParliaSettings.LABEL_COPY_TEXT)
        button.clicked.connect(lambda: copy_text(self.transcription_panel))
        return button

    def create_file_row(self):
        """
        Create second row with one button:
        - "Ajouter des fichiers à la requête"
        """
        layout = QHBoxLayout()

        button_add_files = QPushButton(ParliaSettings.LABEL_ADD_FILES)
        button_add_files.clicked.connect(
            lambda: add_files_to_text_area(self.transcription_panel.transcription_text)
        )
        layout.addWidget(button_add_files)

        return layout

    def create_focus_row(self):
        """
        Create third row with six buttons:
        - "Focus vers ChatGPT"
        - "Focus vers VS Code"
        - "Focus et Code"
        - "Focus and Refacto"
        - "Expliquer le code"
        - "Analyser le code"
        """
        layout = QHBoxLayout()
        layout.addWidget(self.create_focus_chatgpt_button())
        layout.addWidget(self.create_focus_vscode_button())
        layout.addWidget(self.create_focus_and_code_button())
        layout.addWidget(self.create_focus_and_refacto_button())
        layout.addWidget(self.create_explain_code_button())
        layout.addWidget(self.create_analyze_code_button())
        return layout

    def create_focus_chatgpt_button(self):
        """
        Create the "Focus vers ChatGPT" button.
        """
        button = QPushButton(ParliaSettings.LABEL_FOCUS_CHATGPT)
        button.clicked.connect(
            lambda: send_text_to_chatgpt(
                text=self.transcription_panel.get_transcription_text(),
                status_callback=self.show_status_message,
            )
        )
        return button

    def create_focus_vscode_button(self):
        """
        Create the "Focus vers VS Code" button.
        """
        button = QPushButton(ParliaSettings.LABEL_FOCUS_VSCODE)
        button.clicked.connect(
            lambda: focus_vscode_qt(
                text=self.transcription_panel.get_transcription_text(),
                status_callback=self.show_status_message,
                countdown_callback=self.show_countdown_message,
            )
        )
        return button

    def create_focus_and_code_button(self):
        """
        Create the "Focus et Code" button.
        """
        button = QPushButton(ParliaSettings.LABEL_FOCUS_AND_CODE)
        button.clicked.connect(
            lambda: focus_and_paste_in_vscode(
                text=config.focus_and_code,
                status_callback=self.show_status_message,
                countdown_callback=self.show_countdown_message,
            )
        )

        return button

    def create_focus_and_refacto_button(self):
        """
        Create the "Focus and Refacto" button.
        """
        button = QPushButton(ParliaSettings.LABEL_FOCUS_AND_REFACTO)

        button.clicked.connect(
            lambda: focus_vscode_and_refacto(
                text=self.transcription_panel.get_transcription_text(),
                status_callback=self.show_status_message,
                countdown_callback=self.show_countdown_message,
            )
        )
        return button

    def create_explain_code_button(self):
        """
        Create the "Expliquer le code" button.
        """
        button = QPushButton(ParliaSettings.LABEL_EXPLAIN_CODE)
        button.clicked.connect(
            lambda: explain_code_to_vscode(
                method_name=self.transcription_panel.get_transcription_text(),
                status_callback=self.show_status_message,
                countdown_callback=self.show_countdown_message,
            )
        )
        return button

    def create_analyze_code_button(self):
        """
        Create the "Analyser le code" button.
        """
        button = QPushButton(ParliaSettings.LABEL_ANALYZE_CODE)
        button.clicked.connect(
            lambda: analyze_code_to_vscode(
                status_callback=self.show_status_message,
                countdown_callback=self.show_countdown_message,
            )
        )
        return button

    def show_status_message(self, message: str, success: bool = True):
        """
        Update the status label with the provided message.
        Change the color based on success or failure.
        """
        self.status_label.setText(message)
        color = "green" if success else "red"
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def show_countdown_message(self, message: str):
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: orange; font-style: italic;")
