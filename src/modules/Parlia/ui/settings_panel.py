# 🧩 Composant : SettingsPanel
# Ce widget représente le panneau de configuration des modèles Whisper.
# Il est intégré dans ParliaHome, et gère :
# - la sélection du dossier contenant les modèles
# - l'affichage des modèles disponibles dans ce dossier
# - le choix du modèle à charger

import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from modules.parlia.core.whisper_manager import load_model


# 📦 Classe principale : SettingsPanel hérite de QWidget
# - Prend le parent (généralement ParliaHome) en paramètre
# - Initialise l’interface et les interactions
# - Utilise un layout vertical
class SettingsPanel(QWidget):
    def __init__(self, parent=None):
        # Appeler le constructeur parent
        super().__init__(parent)
        # Initialiser les attributs : dossier sélectionné, liste des modèles disponibles
        self.current_folder = None
        self.model_list = []
        # Construire le layout avec :
        # - Un label "Modèle en cours :"
        # - Un bouton "Choisir dossier"
        # - Une ComboBox (invisible tant qu’aucun dossier n’est choisi)
        # - Un QLabel facultatif pour le chemin ou les erreurs
        self._build_ui()

    # 🔧 Méthode privée _build_ui(self)
    # - Crée et configure les composants de l'interface
    # - Connecte les signaux nécessaires
    # - Par défaut, la ComboBox des modèles est cachée
    def _build_ui(self):
        """Crée et configure les composants de l'interface."""
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Label pour le modèle en cours
        self.current_model_label = QLabel("Modèle en cours : Aucun")
        self.main_layout.addWidget(self.current_model_label)

        # Bouton pour choisir un dossier
        self.select_folder_button = QPushButton("Choisir dossier")
        self.select_folder_button.clicked.connect(self._select_model_folder)
        self.main_layout.addWidget(self.select_folder_button)

        # ComboBox pour les modèles disponibles
        self.model_combobox = QComboBox()
        self.model_combobox.setVisible(False)
        self.model_combobox.currentTextChanged.connect(self._on_model_selected)
        self.main_layout.addWidget(self.model_combobox)

        # Label pour afficher le chemin ou les erreurs
        self.path_label = QLabel("")
        self.path_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.path_label)

    # 📂 Méthode : _select_model_folder(self)
    # - Ouvre un QFileDialog pour choisir un dossier
    # - Met à jour l’attribut dossier courant
    # - Appelle _update_model_list() pour scanner le contenu
    def _select_model_folder(self):
        """Ouvre un QFileDialog pour choisir un dossier."""
        folder = QFileDialog.getExistingDirectory(self, "Choisir un dossier")
        if folder:
            self.current_folder = folder
            self.path_label.setText(f"Dossier sélectionné : {folder}")
            self._update_model_list()

    # 📜 Méthode : _update_model_list(self)
    # - Liste les fichiers ou dossiers dans le dossier sélectionné
    # - Filtre selon extension (ex: .pt, .bin) ou sous-dossiers
    # - Met à jour la ComboBox
    # - Affiche la ComboBox uniquement s’il y a des résultats
    def _update_model_list(self):
        """Liste les fichiers ou dossiers dans le dossier sélectionné."""
        if not self.current_folder or not os.path.isdir(self.current_folder):
            self.path_label.setText("Erreur : Dossier invalide.")
            self.model_combobox.setVisible(False)
            return

        # Filtrer les fichiers avec extensions spécifiques
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

    # 🎯 Méthode : _on_model_selected(self, model_name: str)
    # - Appelée quand l’utilisateur sélectionne un modèle dans la ComboBox
    # - Peut appeler whisper_manager.load_model(model_name) plus tard
    # - Affiche un message de confirmation ou de debug
    def _on_model_selected(self, model_name):
        """Appelée quand l’utilisateur sélectionne un modèle dans la ComboBox."""
        if model_name:
            load_model(model_name)
            self.current_model_label.setText(f"Modèle en cours : {model_name}")
            print(f"Modèle '{model_name}' sélectionné et chargé.")
