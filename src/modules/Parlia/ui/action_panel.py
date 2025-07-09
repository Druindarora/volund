from PySide6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget

from modules.parlia.services.action_service import copy_chatrelay_text, copy_text
from modules.parlia.ui.transcription_panel import TranscriptionPanel


class ActionPanel(QWidget):
    def __init__(self, transcription_panel: TranscriptionPanel, parent=None):
        super().__init__(parent)
        self.transcription_panel = transcription_panel

        # Create the main vertical layout for the action panel
        main_layout = QVBoxLayout()

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
        button = QPushButton("Focus vers ChatGPT")
        # Connect signal if needed
        return button

    def create_focus_vscode_button(self):
        """
        Create the "Focus vers VS Code" button.
        """
        button = QPushButton("Focus vers VS Code")
        # Connect signal if needed
        return button

    def create_focus_and_code_button(self):
        """
        Create the "Focus et Code" button.
        """
        button = QPushButton("Focus et Code")
        # Connect signal if needed
        return button

    def create_focus_and_refacto_button(self):
        """
        Create the "Focus and Refacto" button.
        """
        button = QPushButton("Focus and Refacto")
        # Connect signal if needed
        return button
