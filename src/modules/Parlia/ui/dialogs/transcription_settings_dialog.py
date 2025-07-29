from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from modules.parlia.i18n.parlia_strings import ParliaStrings
from modules.parlia.services.parlia_data import (
    get_conclusion_text,
    get_include_conclusion,
    set_conclusion_text,
    set_include_conclusion,
)


class TranscriptionSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Configuration de la fenêtre
        self.setWindowTitle("Transcription Settings")
        self.resize(400, 300)  # Taille par défaut

        # Layout principal
        layout = QVBoxLayout(self)

        # Checkbox d'activation
        self.include_conclusion_checkbox = QCheckBox(
            ParliaStrings.Settings.INCLUDE_CONCLUSION, self
        )
        self.include_conclusion_checkbox.setChecked(get_include_conclusion())
        self.include_conclusion_checkbox.stateChanged.connect(
            self._on_include_conclusion_changed
        )
        layout.addWidget(self.include_conclusion_checkbox)

        # Phrase actuelle (readonly)
        self.current_phrase_display = QLabel(self)
        self.current_phrase_display.setText(get_conclusion_text())
        self.current_phrase_display.setStyleSheet("color: gray;")
        layout.addWidget(self.current_phrase_display)

        # Champ pour nouvelle phrase
        self.custom_phrase_input = QLineEdit(self)
        self.custom_phrase_input.setPlaceholderText(
            ParliaStrings.Settings.PLACEHOLDER_CUSTOM_PHRASE
        )
        layout.addWidget(self.custom_phrase_input)

        # Bouton d'enregistrement
        self.new_phrase_button = QPushButton("💾 Enregistrer la phrase", self)
        self.new_phrase_button.clicked.connect(self._on_new_phrase_clicked)
        layout.addWidget(self.new_phrase_button)

        # Boutons OK / Annuler
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def _on_include_conclusion_changed(self, state: Qt.CheckState):
        is_checked = state == Qt.CheckState.Checked
        set_include_conclusion(is_checked)
        self.current_phrase_display.setEnabled(is_checked)
        self.new_phrase_button.setEnabled(is_checked)
        self.custom_phrase_input.setEnabled(is_checked)

    def _on_new_phrase_clicked(self):
        custom_phrase = self.custom_phrase_input.text()
        set_conclusion_text(custom_phrase)
        self.current_phrase_display.setText(custom_phrase)
        self.custom_phrase_input.clear()
