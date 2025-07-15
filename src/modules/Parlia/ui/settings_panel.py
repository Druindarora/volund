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
from modules.parlia.services.parlia_data import (
    get_conclusion_text,
    get_include_conclusion,
    get_model_folder_path,
    get_model_name,
    set_conclusion_text,  # Importer la fonction pour sauvegarder le texte de conclusion
    set_include_conclusion,  # Importer la fonction pour sauvegarder l'état de la checkbox
    set_model_folder_path,  # Importer la fonction pour sauvegarder le dossier modèle
)


class SettingsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_folder = None
        self.model_list = []
        self._load_user_preferences()
        self._build_ui()

    def _load_user_preferences(self):
        """
        Charger les préférences utilisateur sauvegardées.
        """
        # Charger le chemin du dossier modèle
        self.current_folder = get_model_folder_path()

        # Charger le nom du modèle sélectionné
        self.selected_model_name = get_model_name()

        # Charger l'état de la case à cocher pour la phrase de conclusion
        self.include_conclusion_state = get_include_conclusion()

        # Charger le texte de la phrase de conclusion
        self.custom_conclusion_phrase = get_conclusion_text()

    def _build_ui(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.current_model_label = QLabel("Modèle en cours : Aucun")
        if self.selected_model_name:
            self.current_model_label.setText(
                f"Modèle en cours : {self.selected_model_name}"
            )
        self.main_layout.addWidget(self.current_model_label)

        self.select_folder_button = QPushButton("Choisir dossier")
        self.select_folder_button.clicked.connect(self._select_model_folder)
        self.main_layout.addWidget(self.select_folder_button)

        self.model_combobox = QComboBox()
        self.model_combobox.setVisible(False)
        self.model_combobox.currentTextChanged.connect(self._on_model_selected)
        if self.current_folder and os.path.isdir(self.current_folder):
            self._update_model_list()
            if self.selected_model_name in self.model_list:
                self.model_combobox.setCurrentText(self.selected_model_name)
                self.model_combobox.setVisible(True)
        self.main_layout.addWidget(self.model_combobox)

        self.path_label = QLabel("")
        self.path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.current_folder:
            self.path_label.setText(f"Dossier sélectionné : {self.current_folder}")
        self.main_layout.addWidget(self.path_label)

        self._add_conclusion_phrase_section()

    def _select_model_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choisir un dossier")
        if folder:
            self.current_folder = folder

            # Sauvegarder le dossier sélectionné dans parlia_data
            set_model_folder_path(folder)

            # Mettre à jour l’étiquette pour afficher le chemin choisi
            self.path_label.setText(f"Dossier sélectionné : {folder}")

            # Appeler _update_model_list() pour lister les fichiers de modèles du dossier
            self._update_model_list()

    def _update_model_list(self):
        if not self.current_folder or not os.path.isdir(self.current_folder):
            self.path_label.setText("Erreur : Dossier invalide.")
            self.model_combobox.setVisible(False)
            return

        # Afficher tous les fichiers finissant par .pt ou .bin
        self.model_list = [
            f for f in os.listdir(self.current_folder) if f.endswith((".pt", ".bin"))
        ]

        if self.model_list:
            self.model_combobox.clear()
            self.model_combobox.addItems(self.model_list)
            self.model_combobox.setVisible(True)

            # Sélectionner automatiquement le modèle sauvegardé
            if self.selected_model_name in self.model_list:
                self.model_combobox.setCurrentText(self.selected_model_name)
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

        # Désactiver les signaux pendant l'initialisation pour éviter les erreurs
        self.include_conclusion_checkbox.blockSignals(True)
        if self.include_conclusion_state is not None:
            self.include_conclusion_checkbox.setChecked(self.include_conclusion_state)
        self.include_conclusion_checkbox.blockSignals(False)

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
        self.custom_phrase_input.textChanged.connect(self._on_custom_phrase_changed)
        conclusion_layout.addWidget(self.custom_phrase_input)

        self.main_layout.addLayout(conclusion_layout)

        # Appliquer manuellement l'état une fois tous les éléments créés
        self._on_include_conclusion_changed(
            self.include_conclusion_checkbox.checkState()
        )

        # Placeholder methods for future implementation

    def _on_include_conclusion_changed(self, state):
        # Sauvegarder l’état de la checkbox dans parlia_data
        set_include_conclusion(bool(state))

        if state:  # Si cochée
            self.current_phrase_display.setEnabled(True)
            self.new_phrase_button.setEnabled(True)
            self.custom_phrase_input.setEnabled(True)

            conclusion_text = get_conclusion_text()
            if conclusion_text:
                self.current_phrase_display.setText(conclusion_text)
            else:
                self.current_phrase_display.setText("Aucun")
        else:  # Si décochée
            self.current_phrase_display.setEnabled(False)
            self.new_phrase_button.setEnabled(False)
            self.custom_phrase_input.setEnabled(False)

            self.current_phrase_display.setText("Aucun")

    def _on_new_phrase_clicked(self):
        print("New phrase button clicked")
        self._save_custom_phrase()  # Appeler la méthode de sauvegarde

    def _on_custom_phrase_changed(self, text):
        """
        Permettre à l'utilisateur d'éditer librement une nouvelle phrase sans sauvegarde automatique.
        """
        self.current_phrase_display.setText(text)

    def _save_custom_phrase(self):
        """
        Sauvegarder la phrase personnalisée lorsque l'utilisateur clique sur le bouton "Nouvelle phrase".
        """
        custom_phrase = self.custom_phrase_input.text()

        # Sauvegarder le texte via set_conclusion_text
        set_conclusion_text(custom_phrase)

        # Mettre à jour l'affichage dans current_phrase_display
        self.current_phrase_display.setText(custom_phrase)

        # Optionnel : Remplacer la valeur dans custom_phrase_input par ""
        self.custom_phrase_input.clear()
