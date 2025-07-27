# === FICHIER : settings_panel.py ===
# 🔍 Audit du panneau de configuration principal de Parlia
# --------------------------------------------------
# ✅ Rôle : choisir le dossier de modèles, le modèle actif, et gérer la phrase de conclusion
# 📁 Composant logique dans `ui/` (lié à la persistance utilisateur)
# --------------------------------------------------

# ✅ Points positifs :
# - Interface claire et modulaire (sections bien séparées)
# - Rétention des choix utilisateur cohérente (dossier + modèle + conclusion)
# - Intégration avec `parlia_data` et `whisper_service` propre

# 🔄 Propositions d’amélioration :
# 1. 🔁 Extraire la **phrase de conclusion** dans un `transcription_dialog.py` (comme discuté)
# 2. 🔁 Extraire `model_selection` dans un widget réutilisable : `ModelSelectorWidget`
#    (utile si d’autres IA sont ajoutées : IA de code, IA secondaire, etc.)
# 3. ✅ Lister les fichiers modèles de manière asynchrone si ça devient lent
# 4. 🧹 Supprimer `set_conclusion_text(...)` (doublon inutile de `self._save_custom_phrase()`)

# 🟡 Code un peu long (>300 lignes), mais chaque bloc est bien isolé.
# Lorsque `dialog_transcription.py` sera en place, tu pourras couper facilement ~100 lignes.

# ✅ À conserver tel quel pour l’instant. Il sert bien son rôle jusqu’à la prochaine refonte UI.

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from modules.parlia.core.whisper_manager import (
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
from modules.parlia.services.whisper_service import whisper_service
from modules.parlia.settings import ParliaSettings
from modules.parlia.utils.stylesheet_loader import load_qss_for


class SettingsPanel(QWidget):
    def __init__(self, update_record_callback=None, parent=None):
        super().__init__(parent)
        self.update_record_callback = update_record_callback
        self.current_folder = None
        self.model_list = []
        self._load_user_preferences()
        self._build_ui()
        load_qss_for(self)

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

        # Ajouter la section de la phrase de conclusion
        self._add_conclusion_phrase_section()

    def _add_model_section(self):
        """
        Section du modèle : bouton + chemin, puis combo + label en ligne.
        """
        # Ligne : bouton + chemin
        folder_line_layout = QHBoxLayout()

        self.select_folder_button = QPushButton(ParliaSettings.LABEL_CHOOSE_FOLDER)
        self.select_folder_button.setObjectName("SelectFolderButton")
        self.select_folder_button.clicked.connect(self._select_model_folder)
        folder_line_layout.addWidget(self.select_folder_button)

        self.path_label = QLabel()
        self.path_label.setObjectName("PathLabel")
        self.path_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._update_path_label()
        folder_line_layout.addWidget(self.path_label)

        self.main_layout.addLayout(folder_line_layout)

        self.main_layout.addSpacing(10)

        # ✅ Ligne combo + label
        model_line_layout = QHBoxLayout()

        # Label "Modèle sélectionné :"
        label = QLabel("Modèle sélectionné :")
        label.setObjectName("ModelLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        label.setFixedWidth(150)  # 🔧 Largeur fixe raisonnable pour bien l’aligner

        # ComboBox juste à côté
        self.model_combobox = QComboBox(self)
        self.model_combobox.setObjectName("ModelComboBox")
        self.model_combobox.setWindowFlags(Qt.WindowType.Widget)
        self.model_combobox.setVisible(False)
        self.model_combobox.currentTextChanged.connect(self._on_model_selected)
        self.model_combobox.setFixedWidth(220)  # 🔧 Largeur fixe élégante

        # Ajout dans layout horizontal
        model_line_layout.addWidget(label)
        model_line_layout.addSpacing(10)  # 🔧 Petit écart visuel
        model_line_layout.addWidget(self.model_combobox)
        model_line_layout.addStretch()  # ✅ Repousse le reste à droite

        self.main_layout.addLayout(model_line_layout)

        # ✅ Chargement des modèles si dossier déjà connu
        if self.current_folder and os.path.isdir(self.current_folder):
            self._update_model_list()
            self._set_initial_model_selection()

    def _update_path_label(self):
        """Met à jour le texte du label du chemin du dossier."""
        if self.current_folder:
            self.path_label.setText(
                ParliaSettings.LABEL_CURRENT_FOLDER.format(folder=self.current_folder)
            )
        else:
            self.path_label.setText("")

    def _set_initial_model_selection(self):
        """Configure la sélection initiale dans la combo box des modèles."""
        if self.selected_model_name in self.model_list:
            self.model_combobox.setCurrentText(self.selected_model_name)
            self.model_combobox.setVisible(True)

    def _add_conclusion_phrase_section(self):
        """
        Ajoute une section claire et structurée pour gérer la phrase de conclusion.
        """
        conclusion_layout = QVBoxLayout()

        # Espacement avant bloc
        self.main_layout.addSpacing(15)

        # 1. Checkbox d'activation
        self.include_conclusion_checkbox = QCheckBox(
            ParliaSettings.LABEL_INCLUDE_CONCLUSION
        )
        self.include_conclusion_checkbox.stateChanged.connect(
            self._on_include_conclusion_changed
        )

        self.include_conclusion_checkbox.blockSignals(True)
        if self.include_conclusion_state is not None:
            self.include_conclusion_checkbox.setChecked(self.include_conclusion_state)
        self.include_conclusion_checkbox.blockSignals(False)
        conclusion_layout.addWidget(self.include_conclusion_checkbox)

        # 2. Ligne : Phrase actuelle (label + champ readonly)
        current_phrase_layout = QHBoxLayout()
        self.current_label = QLabel("Phrase actuelle :")  # 🔧 deviens attribut
        self.current_label.setStyleSheet("font-weight: bold;")
        self.current_phrase_display = QLineEdit()
        self.current_phrase_display.setReadOnly(True)
        self.current_phrase_display.setStyleSheet("color: gray;")
        current_phrase_layout.addWidget(self.current_label)
        current_phrase_layout.addWidget(self.current_phrase_display)
        conclusion_layout.addLayout(current_phrase_layout)

        # 3. Ligne : Nouvelle phrase (label + champ modifiable)
        new_phrase_layout = QHBoxLayout()
        self.new_phrase_label = QLabel("Nouvelle phrase :")  # 🔧 deviens attribut
        self.new_phrase_label.setStyleSheet("font-weight: bold;")
        self.custom_phrase_input = QLineEdit()
        self.custom_phrase_input.setPlaceholderText(
            ParliaSettings.LABEL_PLACEHOLDER_CUSTOM_PHRASE
        )
        new_phrase_layout.addWidget(self.new_phrase_label)
        new_phrase_layout.addWidget(self.custom_phrase_input)
        conclusion_layout.addLayout(new_phrase_layout)

        # 4. Bouton d’enregistrement
        self.new_phrase_button = QPushButton("💾 Enregistrer la phrase")
        self.new_phrase_button.clicked.connect(self._on_new_phrase_clicked)
        conclusion_layout.addWidget(self.new_phrase_button)

        # Intégrer dans le layout principal
        self.main_layout.addLayout(conclusion_layout)

        # Appliquer l’état initial
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

        # ✅ On désactive ou réactive les labels également
        self.current_label.setEnabled(is_checked)
        self.new_phrase_label.setEnabled(is_checked)

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

            if self.update_record_callback:
                self.update_record_callback()

            return

        if model_name:
            print(f"Modèle sélectionné _on_model_selected : {model_name}")
            set_model_name(model_name)

            whisper_service.load_model_async(
                model_name, on_finished=self.update_record_callback
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

    def apply_ui_state(self):
        """
        Méthode obligatoire pour que ParliaStateManager puisse rafraîchir l'état des composants enregistrés.
        Ici, on ne fait rien car SettingsPanel n'a pas de logique d'état dynamique.
        """
        pass
