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

from modules.parlia.core.whisper_manager import (
    load_model,
    unload_model,
)
from modules.parlia.services.parlia_data import (
    get_conclusion_text,
    get_include_conclusion,
    get_model_folder_path,
    get_model_name,
    set_conclusion_text,
    set_include_conclusion,
    set_model_folder_path,
    set_model_name,
)
from modules.parlia.settings import ParliaSettings


class SettingsPanel(QWidget):
    def __init__(self, update_record_callback=None, parent=None):
        super().__init__(parent)
        self.update_record_callback = update_record_callback
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
        """
        Construire l'interface utilisateur principale.
        """
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Ajouter la section du modèle
        self._add_model_section()

        # Ajouter la section du chemin du dossier
        self._add_folder_path_section()

        # Ajouter la section de la phrase de conclusion
        self._add_conclusion_phrase_section()

    def _add_model_section(self):
        """
        Ajouter la section pour le modèle sélectionné.
        """
        self.current_model_label = QLabel(ParliaSettings.LABEL_CURRENT_MODEL)
        if self.selected_model_name:
            self.current_model_label.setText(
                ParliaSettings.LABEL_CURRENT_MODEL.format(
                    model_name=self.selected_model_name
                )
            )
        self.main_layout.addWidget(self.current_model_label)

        self.select_folder_button = QPushButton(ParliaSettings.LABEL_CHOOSE_FOLDER)
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

    def _add_folder_path_section(self):
        """
        Ajouter la section pour afficher le chemin du dossier sélectionné.
        """
        self.path_label = QLabel("")
        self.path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.current_folder:
            self.path_label.setText(
                ParliaSettings.LABEL_CHOOSE_FOLDER.format(folder=self.current_folder)
            )
        self.main_layout.addWidget(self.path_label)

    def _add_conclusion_phrase_section(self):
        """
        Add a section to configure the 'phrase de conclusion'.
        """
        conclusion_layout = QVBoxLayout()

        # Checkbox for automatic inclusion
        self.include_conclusion_checkbox = QCheckBox(
            ParliaSettings.LABEL_INCLUDE_CONCLUSION
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
        current_phrases_label = QLabel(ParliaSettings.LABEL_CURRENT_CONCLUSION_PHRASES)
        conclusion_layout.addWidget(current_phrases_label)

        # Non-editable field for current phrase
        self.current_phrase_display = QLineEdit(
            ParliaSettings.LABEL_NO_CURRENT_CONCLUSION
        )
        self.current_phrase_display.setReadOnly(True)
        conclusion_layout.addWidget(self.current_phrase_display)

        # Button to randomize or reset the phrase
        self.new_phrase_button = QPushButton(ParliaSettings.LABEL_NEW_PHRASE)
        self.new_phrase_button.clicked.connect(self._on_new_phrase_clicked)
        conclusion_layout.addWidget(self.new_phrase_button)

        # Editable field for custom phrase
        self.custom_phrase_input = QLineEdit()
        self.custom_phrase_input.setPlaceholderText(
            ParliaSettings.LABEL_PLACEHOLDER_CUSTOM_PHRASE
        )
        conclusion_layout.addWidget(self.custom_phrase_input)

        self.main_layout.addLayout(conclusion_layout)

        # Appliquer manuellement l'état une fois tous les éléments créés
        self._on_include_conclusion_changed(
            Qt.CheckState.Checked
            if self.include_conclusion_state
            else Qt.CheckState.Unchecked
        )

    def _on_include_conclusion_changed(self, state: Qt.CheckState):
        # Sauvegarder l’état de la checkbox dans parlia_data
        is_checked = (
            state == Qt.CheckState.Checked
            or getattr(state, "value", state) == Qt.CheckState.Checked.value
        )
        set_include_conclusion(is_checked)

        # Appliquer l’état visuel des champs associés
        self.current_phrase_display.setEnabled(is_checked)
        self.new_phrase_button.setEnabled(is_checked)
        self.custom_phrase_input.setEnabled(is_checked)

        if is_checked:
            conclusion_text = get_conclusion_text()
            if conclusion_text:
                self.current_phrase_display.setText(conclusion_text)
            else:
                self.current_phrase_display.setText(
                    ParliaSettings.LABEL_NO_CURRENT_CONCLUSION
                )
        else:
            self.current_phrase_display.setText(
                ParliaSettings.LABEL_NO_CURRENT_CONCLUSION
            )

    def _on_new_phrase_clicked(self):
        print("New phrase button clicked")
        self._save_custom_phrase()  # Appeler la méthode de sauvegarde

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

    def _select_model_folder(self):
        """
        Méthode pour gérer la sélection du dossier contenant les modèles.
        """
        folder = QFileDialog.getExistingDirectory(
            self, ParliaSettings.LABEL_CHOOSE_FOLDER
        )
        if folder:
            self.current_folder = folder

            # Sauvegarder le dossier sélectionné dans parlia_data
            set_model_folder_path(folder)

            # Mettre à jour l’étiquette pour afficher le chemin choisi
            self.path_label.setText(
                ParliaSettings.LABEL_CURRENT_FOLDER.format(folder=folder)
            )

            # Appeler _update_model_list() pour lister les fichiers de modèles du dossier
            self._update_model_list()

    def _update_model_list(self):
        """
        Met à jour la liste déroulante avec les modèles disponibles dans le dossier sélectionné.
        - Affiche uniquement les fichiers .pt ou .bin.
        - Sélectionne automatiquement le modèle sauvegardé si présent.
        - Sinon, tente de sélectionner "tiny.pt" ou "tiny.bin" si présent.
        - Sinon, ne sélectionne rien.
        """
        if not self.current_folder or not os.path.isdir(self.current_folder):
            self.path_label.setText(ParliaSettings.LABEL_ERROR_INVALID_FOLDER)
            self.model_combobox.setVisible(False)
            return

        # Liste des fichiers .pt ou .bin
        self.model_list = [
            f for f in os.listdir(self.current_folder) if f.endswith((".pt", ".bin"))
        ]

        if self.model_list:
            self.model_combobox.clear()
            self.model_combobox.addItem(
                ParliaSettings.LABEL_NO_MODEL_SELECTED, userData=None
            )  # Valeur neutre
            self.model_combobox.addItems(self.model_list)
            self.model_combobox.setVisible(True)

            # Sélection modèle sauvegardé ou fallback tiny
            if self.selected_model_name and self.selected_model_name in self.model_list:
                self.model_combobox.setCurrentText(self.selected_model_name)
            elif "tiny.pt" in self.model_list:
                self.model_combobox.setCurrentText("tiny.pt")
            elif "tiny.bin" in self.model_list:
                self.model_combobox.setCurrentText("tiny.bin")
            else:
                # Aucun modèle par défaut trouvé, ne rien sélectionner
                pass
        else:
            self.model_combobox.setVisible(False)
            self.path_label.setText(ParliaSettings.LABEL_NO_MODEL_SELECTED)

    def _on_model_selected(self, model_name):
        """
        Gère la sélection d’un modèle dans la liste déroulante.
        - Si "Aucun modèle sélectionné" : décharge le modèle en cours.
        - Sinon : charge le modèle choisi.
        Met à jour l'affichage et les boutons d’enregistrement.
        """
        if model_name == ParliaSettings.LABEL_NO_MODEL_SELECTED:
            print("[INFO] Aucun modèle sélectionné. Déchargement du modèle en cours.")
            unload_model()
            no_model_name = ParliaSettings.LABEL_NO_MODEL_SELECTED
            set_model_name(no_model_name)
            self.current_model_label.setText(no_model_name)

            if self.update_record_callback:
                self.update_record_callback()

            return

        if model_name:
            print(f"Modèle sélectionné _on_model_selected : {model_name}")
            set_model_name(model_name)
            load_model(model_name)
            self.current_model_label.setText(
                ParliaSettings.LABEL_CURRENT_MODEL.format(model_name=model_name)
            )

            if self.update_record_callback:
                self.update_record_callback()

    def set_conclusion_text(self, custom_phrase: str):
        """
        Sauvegarde la phrase de conclusion personnalisée dans les données utilisateur (fichier parlia.json).
        :param custom_phrase: La phrase de conclusion à sauvegarder.
        """
        if not custom_phrase.strip():
            raise ValueError("La phrase de conclusion ne peut pas être vide.")

        set_conclusion_text(custom_phrase)

        print(f"Phrase de conclusion sauvegardée : {custom_phrase}")
