import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from modules.parlia.services.action_service import copy_chatrelay_text, copy_text
from modules.parlia.services.chatgptService import (
    add_files_to_text_area,
    send_text_to_chatgpt,
)

# from modules.parlia.services.parlia_data import get_prompt_code_vs_code
from modules.parlia.services.parlia_data import get_prompt
from modules.parlia.services.parlia_state_manager import parlia_state
from modules.parlia.services.vsCodeService import (
    analyze_code_to_vscode,
    explain_code_to_vscode,
    focus_and_paste_in_vscode,
    focus_vscode_and_refacto,
    focus_vscode_qt,
)
from modules.parlia.settings import ParliaSettings
from modules.parlia.ui.dialogs.prompt_editor_dialog import PromptEditorDialog
from modules.parlia.ui.transcription_panel import TranscriptionPanel
from modules.parlia.utils.stylesheet_loader import load_qss_for


class ActionPanel(QWidget):
    def __init__(self, transcription_panel: TranscriptionPanel, parent=None):
        super().__init__(parent)
        self.transcription_panel = transcription_panel

        main_layout = QVBoxLayout()

        # Status label en haut
        self.status_label = QLabel(ParliaSettings.LABEL_READY)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)

        # Bouton paramètres (à droite du label)
        self._add_prompt_settings_button(main_layout)

        # First row
        row1 = self.create_row_one()
        main_layout.addLayout(row1)

        # Second row
        row2 = self.create_row_two()
        main_layout.addLayout(row2)

        # Third row
        row3 = self.create_row_three()
        main_layout.addLayout(row3)

        self.setLayout(main_layout)

        load_qss_for(self)
        parlia_state.register_ui_component(self)

    def _add_prompt_settings_button(self, layout: QVBoxLayout):
        settings_button = QPushButton()
        settings_button.setIcon(qta.icon("fa5s.cog", color="#E5E5E5"))
        settings_button.setToolTip("Modifier les prompts personnalisés")
        settings_button.setFixedSize(32, 32)
        settings_button.clicked.connect(self.open_prompt_editor)

        header_layout = QHBoxLayout()
        header_layout.addWidget(self.status_label)
        header_layout.addStretch()
        header_layout.addWidget(settings_button)

        layout.addLayout(header_layout)

    def create_row_one(self):
        """
        Create first row with two buttons:
        - "Copier vers ChatRelay"
        - "Copier le texte"
        """
        layout = QHBoxLayout()
        layout.addWidget(self.create_chatrelay_button())
        layout.addWidget(self.create_copy_text_button())
        layout.addWidget(self.create_add_files_button())
        return layout

    def create_chatrelay_button(self):
        """
        Create the "Copier [ChatRelay]" button.
        """
        button = QPushButton(ParliaSettings.LABEL_CHATRELAY)
        button.setIcon(qta.icon("fa5s.paper-plane", color="#333333"))
        button.setObjectName("chatRelayButton")
        button.clicked.connect(copy_chatrelay_text)
        return button

    def create_copy_text_button(self):
        """
        Create the "Copier le texte" button.
        """
        button = QPushButton(ParliaSettings.LABEL_COPY_TEXT)
        button.setIcon(qta.icon("fa5s.copy", color="#333333"))
        button.setObjectName("copyTextButton")
        button.clicked.connect(lambda: copy_text(self.transcription_panel))
        return button

    def create_add_files_button(self):
        button_add_files = QPushButton(ParliaSettings.LABEL_ADD_FILES)
        button_add_files.setIcon(qta.icon("fa5s.file-medical", color="#333333"))
        button_add_files.setObjectName("addFilesButton")
        button_add_files.clicked.connect(
            lambda: add_files_to_text_area(self.transcription_panel.transcription_text)
        )
        return button_add_files

    def create_row_two(self):
        """
        Create second row with one button:
        - "Ajouter des fichiers à la requête"
        """
        layout = QHBoxLayout()
        layout.addWidget(self.create_focus_chatgpt_button())
        layout.addWidget(self.create_focus_vscode_button())
        layout.addWidget(self.create_focus_and_code_button())
        return layout

    def create_focus_chatgpt_button(self):
        """
        Create the "Focus vers ChatGPT" button.
        """
        button = QPushButton(ParliaSettings.LABEL_FOCUS_CHATGPT)
        button.setIcon(qta.icon("fa5s.comment-dots", color="#333333"))
        button.setObjectName("focusChatGPTButton")
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
        button.setIcon(qta.icon("fa5s.terminal", color="#333333"))
        button.setObjectName("focusVSCodeButton")
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
        button.setIcon(qta.icon("fa5s.clipboard", color="#333333"))
        button.setObjectName("focusAndCodeButton")
        button.clicked.connect(
            lambda: focus_and_paste_in_vscode(
                text=get_prompt("prompt_code_comments"),
                status_callback=self.show_status_message,
                countdown_callback=self.show_countdown_message,
            )
        )
        return button

    def create_row_three(self):
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
        layout.addWidget(self.create_focus_and_refacto_button())
        layout.addWidget(self.create_explain_code_button())
        layout.addWidget(self.create_analyze_code_button())
        layout.addWidget(self.create_generate_tests_button())
        return layout

    def create_focus_and_refacto_button(self):
        """
        Create the "Focus and Refacto" button.
        """
        button = QPushButton(ParliaSettings.LABEL_FOCUS_AND_REFACTO)
        button.setIcon(qta.icon("fa5s.magic", color="#333333"))
        button.setObjectName("focusAndRefactoButton")
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
        button.setIcon(qta.icon("fa5s.question-circle", color="#333333"))
        button.setObjectName("explainCodeButton")
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
        button.setIcon(qta.icon("fa5s.bug", color="#333333"))
        button.setObjectName("analyzeCodeButton")
        button.clicked.connect(
            lambda: analyze_code_to_vscode(
                status_callback=self.show_status_message,
                countdown_callback=self.show_countdown_message,
            )
        )
        return button

    def create_generate_tests_button(self):
        """
        Create the "Générer des tests" button.
        """
        button = QPushButton("Générer des tests")
        button.setIcon(qta.icon("fa5s.vial", color="#333333"))
        button.setObjectName("generateTestsButton")
        # button.clicked.connect(
        #     lambda: self.generate_tests()
        # )
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

    def apply_ui_state(self):
        is_locked = parlia_state.is_ui_locked()
        for button in self.findChildren(QPushButton):
            button.setEnabled(not is_locked)

    def closeEvent(self, event):
        self.__deleted__ = True
        try:
            parlia_state.unregister_ui_component(self)
        except Exception as e:
            print(f"[Panel] Erreur lors du désabonnement : {e}")
        super().closeEvent(event)

    def open_prompt_editor(self):
        dialog = PromptEditorDialog(self)
        dialog.exec_()
