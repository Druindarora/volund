from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from modules.parlia.config import config
from modules.parlia.services.action_service import copy_chatrelay_text, copy_text
from modules.parlia.services.chatgptService import send_text_to_chatgpt
from modules.parlia.services.vsCodeService import (
    focus_and_paste_in_vscode,
    focus_vscode_and_refacto,
    focus_vscode_qt,
)
from modules.parlia.ui.transcription_panel import TranscriptionPanel


class ActionPanel(QWidget):
    def __init__(self, transcription_panel: TranscriptionPanel, parent=None):
        super().__init__(parent)
        self.transcription_panel = transcription_panel

        # Create the main vertical layout for the action panel
        main_layout = QVBoxLayout()

        # Add status label at the top
        self.status_label = QLabel("Prêt")
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
        button = QPushButton("Copier [ChatRelay]")
        button.clicked.connect(copy_chatrelay_text)
        return button

    def create_copy_text_button(self):
        """
        Create the "Copier le texte" button.
        """
        button = QPushButton("Copier le texte")
        button.clicked.connect(lambda: copy_text(self.transcription_panel))
        return button

    def create_file_row(self):
        """
        Create second row with one button:
        - "Ajouter des fichiers à la requête"
        """
        layout = QHBoxLayout()

        button_add_files = QPushButton("Ajouter des fichiers à la requête")
        layout.addWidget(button_add_files)

        return layout

    def create_focus_row(self):
        """
        Create third row with four buttons:
        - "Focus vers ChatGPT"
        - "Focus vers VS Code"
        - "Focus et Code"
        - "Focus and Refacto"
        """
        layout = QHBoxLayout()
        layout.addWidget(self.create_focus_chatgpt_button())
        layout.addWidget(self.create_focus_vscode_button())
        layout.addWidget(self.create_focus_and_code_button())
        layout.addWidget(self.create_focus_and_refacto_button())
        return layout

    def create_focus_chatgpt_button(self):
        """
        Create the "Focus vers ChatGPT" button.
        """
        button = QPushButton("Focus ChatGPT")
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
        button = QPushButton("Focus VSC")
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
        button = QPushButton("Focus VSC et Code")
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
        button = QPushButton("Focus VSC et Refacto")

        button.clicked.connect(
            lambda: focus_vscode_and_refacto(
                text=self.transcription_panel.get_transcription_text(),
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
