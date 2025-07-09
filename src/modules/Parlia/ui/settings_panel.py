# 🧩 Composant : SettingsPanel
# Ce widget représente le panneau de configuration des modèles Whisper.
# Il est intégré dans ParliaHome, et gère :
# - la sélection du dossier contenant les modèles
# - l'affichage des modèles disponibles dans ce dossier
# - le choix du modèle à charger

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from modules.parlia.core.whisper_manager import load_model


class SettingsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_folder = None
        self.model_list = []
        self._build_ui()

    def _build_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.current_model_label = QLabel("Modèle en cours : Aucun")
        self.main_layout.addWidget(self.current_model_label)

        self.select_folder_button = QPushButton("Choisir dossier")
        self.select_folder_button.clicked.connect(self._select_model_folder)
        self.main_layout.addWidget(self.select_folder_button)

        self.model_combobox = QComboBox()
        self.model_combobox.setVisible(False)
        self.model_combobox.currentTextChanged.connect(self._on_model_selected)
        self.main_layout.addWidget(self.model_combobox)

        self.path_label = QLabel("")
        self.path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.path_label)

        self._add_conclusion_phrase_section()

    def _select_model_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choisir un dossier")
        if folder:
            self.current_folder = folder
            self.path_label.setText(f"Dossier sélectionné : {folder}")
            self._update_model_list()

    def _update_model_list(self):
        if not self.current_folder or not os.path.isdir(self.current_folder):
            self.path_label.setText("Erreur : Dossier invalide.")
            self.model_combobox.setVisible(False)
            return

        self.model_list = [
            f for f in os.listdir(self.current_folder) if f.endswith((".pt", ".bin"))
        ]

        if self.model_list:
            self.model_combobox.clear()
            self.model_combobox.addItems(self.model_list)
            self.model_combobox.setVisible(True)
        else:
            self.model_combobox.setVisible(False)
            self.path_label.setText("Aucun modèle trouvé dans le dossier.")

    def _on_model_selected(self, model_name):
        if model_name:
            load_model(model_name)
            self.current_model_label.setText(f"Modèle en cours : {model_name}")
            print(f"Modèle '{model_name}' sélectionné et chargé.")

    def _add_conclusion_phrase_section(self):
        """
        Add a section to configure the 'phrase de conclusion'.
        """
        conclusion_layout = QVBoxLayout()

        # Checkbox for automatic inclusion
        self.include_conclusion_checkbox = QCheckBox(
            "Inclure automatiquement la phrase de conclusion"
        )
        self.include_conclusion_checkbox.stateChanged.connect(
            self._on_include_conclusion_changed
        )
        conclusion_layout.addWidget(self.include_conclusion_checkbox)

        # Label for current phrases
        current_phrases_label = QLabel("Phrases de conclusion actuelles :")
        conclusion_layout.addWidget(current_phrases_label)

        # Non-editable field for current phrase
        self.current_phrase_display = QLineEdit("Aucun")
        self.current_phrase_display.setReadOnly(True)
        conclusion_layout.addWidget(self.current_phrase_display)

        # Button to randomize or reset the phrase
        self.new_phrase_button = QPushButton("Nouvelle phrase")
        self.new_phrase_button.clicked.connect(self._on_new_phrase_clicked)
        conclusion_layout.addWidget(self.new_phrase_button)

        # Editable field for custom phrase
        self.custom_phrase_input = QLineEdit()
        self.custom_phrase_input.setPlaceholderText(
            "Entrez votre phrase de conclusion personnalisée ici..."
        )
        conclusion_layout.addWidget(self.custom_phrase_input)

        self.main_layout.addLayout(conclusion_layout)

    # Placeholder methods for future implementation

    def _on_include_conclusion_changed(self, state):
        print(f"Checkbox state changed: {state}")

    def _on_new_phrase_clicked(self):
        print("New phrase button clicked")
