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

import qtawesome as qta
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,  # Ajout de QPushButton
    QSizePolicy,  # Ajout de QSizePolicy
    QToolButton,  # Réintégration de QToolButton
    QVBoxLayout,
    QWidget,
)

from modules.parlia.i18n.parlia_strings import ParliaStrings

# from modules.parlia.services.code_assistant_service import CodeAssistantService
from modules.parlia.services.ollama_service import OllamaService
from modules.parlia.services.whisper_model_service import WhisperModelService
from modules.parlia.ui.dialogs.settings_preferences_dialog import PreferencesDialog
from modules.parlia.utils.stylesheet_loader import load_qss_for
from src.core.logger_manager import get_logger

logger = get_logger("SettingsPanel")


class SettingsPanel(QWidget):
    def __init__(self, update_record_callback=None, parent=None):
        super().__init__(parent)
        self.update_record_callback = update_record_callback
        self.current_folder = None
        self.model_list = []
        self.ollama_service = OllamaService()
        self.whisper_model_service = WhisperModelService()  # Initialisation du service
        self._load_user_preferences()

        # Construire l'interface utilisateur principale
        self._build_ui()
        load_qss_for(self)

        # Appeler les méthodes pour initialiser la liste des modèles et la sélection
        # self._update_model_list()
        self.whisper_model_service.initializeModel(callback=self._afterModelSelected)
        self.apply_ui_state()  # Appliquer l'état initial de l'interface utilisateur

    def _load_user_preferences(self):
        """
        Charger les préférences utilisateur sauvegardées via WhisperModelService.
        """
        # Charger le chemin du dossier modèle
        self.current_folder = self.whisper_model_service.modelFolder

        # Charger le nom du modèle sélectionné
        self.selected_model_name = self.whisper_model_service.getSelectedModel()

    def _build_ui(self):
        """
        Construire l'interface utilisateur principale avec un header en haut
        et trois blocs côte à côte : Whisper, Ollama, et Assistant de codage.
        """
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # Ajouter l'en-tête en haut
        self._add_header()

        # Créer un layout horizontal pour les blocs
        self.blocks_layout = QHBoxLayout()

        # Créer les trois blocs principaux
        whisper_block = self._create_whisper_block()
        ollama_block = self._create_ollama_block()
        code_assistant_block = self._create_code_assistant_block()

        # Ajouter les blocs au layout horizontal
        self.blocks_layout.addWidget(whisper_block)
        self.blocks_layout.addWidget(ollama_block)
        self.blocks_layout.addWidget(code_assistant_block)

        # Ajouter le layout horizontal au layout principal
        self.main_layout.addLayout(self.blocks_layout)

        # Rendre les blocs responsives
        whisper_block.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        ollama_block.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        code_assistant_block.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )

    def _set_status(self, value_label, text, status_type):
        """
        Met à jour uniquement la valeur colorée d'un QLabel de statut dynamique.
        """
        colors = {
            "ready": "green",
            "error": "red",
            "warning": "orange",
            "neutral": "gray",
            "starting": "orange",  # Ajout de la couleur pour le statut "starting"
        }
        color = colors.get(status_type, "white")
        value_label.setText(text)
        value_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def _create_whisper_block(self):
        """
        Crée le bloc pour Whisper avec un titre, un label de statut et une combo box.
        """
        whisper_widget = QWidget()
        whisper_layout = QVBoxLayout()
        whisper_widget.setLayout(whisper_layout)

        # Titre
        title = QLabel("🎤 Modèle Whisper")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        whisper_layout.addWidget(title)

        # Labels de statut côte à côte
        status_layout = QHBoxLayout()
        static_label = QLabel("Statut :")
        static_label.setStyleSheet("color: white; font-weight: bold;")
        static_label.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred
        )

        self.whisperStatusValue = QLabel("Inactif")
        self.whisperStatusValue.setStyleSheet("color: red; font-weight: bold;")
        self.whisperStatusValue.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred
        )

        status_layout.addWidget(static_label)
        status_layout.addWidget(self.whisperStatusValue)
        status_layout.addStretch()  # pousse l'espace libre après les labels
        whisper_layout.addLayout(status_layout)

        # ComboBox pour les modèles Whisper
        # self.whisperModelComboBox = QComboBox(self)
        # self.whisperModelComboBox.setObjectName("WhisperModelComboBox")
        # self.whisperModelComboBox.setVisible(True)
        # self.whisperModelComboBox.setFixedSize(220, 32)
        # self.whisperModelComboBox.currentTextChanged.connect(self._on_model_selected)
        # whisper_layout.addWidget(self.whisperModelComboBox)

        whisper_layout.setSpacing(10)
        whisper_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        return whisper_widget

    def _create_ollama_block(self):
        """
        Crée le bloc pour Ollama avec un titre, un label de statut et un bouton.
        """
        ollama_widget = QWidget()
        ollama_layout = QVBoxLayout()
        ollama_widget.setLayout(ollama_layout)

        # Titre
        title = QLabel("🤖 Ollama")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        ollama_layout.addWidget(title)

        # Labels de statut côte à côte
        status_layout = QHBoxLayout()
        static_label = QLabel("Statut :")
        static_label.setStyleSheet("color: white; font-weight: bold;")
        static_label.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred
        )

        self.ollama_status_value = QLabel("Inactif")
        self.ollama_status_value.setStyleSheet("color: red; font-weight: bold;")
        self.ollama_status_value.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred
        )

        status_layout.addWidget(static_label)
        status_layout.addWidget(self.ollama_status_value)
        status_layout.addStretch()  # pousse l'espace libre après les labels
        ollama_layout.addLayout(status_layout)

        # Bouton pour démarrer Ollama
        self.ollama_start_button = QPushButton("Démarrer Ollama")
        self.ollama_start_button.setFixedSize(220, 32)
        self.ollama_start_button.clicked.connect(self._start_ollama)
        ollama_layout.addWidget(self.ollama_start_button)

        ollama_layout.setSpacing(10)
        ollama_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        return ollama_widget

    def _create_code_assistant_block(self):
        """
        Crée le bloc pour l'Assistant de codage avec un titre, un label de statut et une combo box.
        """
        code_widget = QWidget()
        code_layout = QVBoxLayout()
        code_widget.setLayout(code_layout)

        # Titre
        title = QLabel("💻 Assistant de codage")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        code_layout.addWidget(title)

        # Label de statut dynamique
        static_label = QLabel("Statut :")
        static_label.setStyleSheet("color: white; font-weight: bold;")
        static_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)

        self.code_status_value = QLabel("Non chargé")
        self.code_status_value.setStyleSheet("color: gray; font-weight: bold;")
        self.code_status_value.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)

        status_layout = QHBoxLayout()
        status_layout.addWidget(static_label)
        status_layout.addWidget(self.code_status_value)
        status_layout.addStretch()
        code_layout.addLayout(status_layout)

        # Chargement des modèles disponibles via CodeAssistantService
        # self.codeAssistantService = CodeAssistantService()
        # available_models = self.codeAssistantService.getAvailableModels()

        # # ComboBox pour les modèles
        # self.code_model_combobox = QComboBox(self)
        # if available_models:
        #     self.code_model_combobox.addItems(available_models)
        # else:
        #     self.code_model_combobox.addItem("Aucun modèle disponible")

        # self.code_model_combobox.setFixedSize(220, 32)
        # self.code_model_combobox.currentTextChanged.connect(
        #     self._on_code_model_selected
        # )
        # code_layout.addWidget(self.code_model_combobox)

        code_layout.setSpacing(10)
        code_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        return code_widget


    def _add_header(self):
        """
        Ajouter un en-tête avec un titre et un bouton engrenage.
        """
        header_layout = QHBoxLayout()

        # Titre "Paramètres"
        title_label = QLabel(ParliaStrings.Home.SETTINGS_TITLE, self)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)

        # Ajouter un stretch pour pousser le bouton engrenage à droite
        header_layout.addStretch()

        # Bouton engrenage
        gear_button = QToolButton(self)
        gear_button.setIcon(qta.icon("fa5s.cog", color="#E5E5E5"))
        gear_button.setToolTip("Ouvrir les préférences")
        gear_button.setFixedSize(32, 32)
        gear_button.clicked.connect(self.open_preferences)
        header_layout.addWidget(gear_button)

        # Ajouter le layout à l'interface principale
        self.main_layout.addLayout(header_layout)

    def open_preferences(self):
        """
        Ouvre la fenêtre PreferencesDialog en modal.
        """
        # preferences_dialog = PreferencesDialog(self)
        # preferences_dialog.exec_()
        preferences_dialog = PreferencesDialog(self)
        preferences_dialog.set_model_selected_callback(self._afterModelSelected)
        preferences_dialog.exec_()

    # def _update_model_list(self):
    #     """
    #     Met à jour la liste des modèles disponibles via WhisperModelService.
    #     """
    #     self.model_list = self.whisper_model_service.listAvailableModels()
    #     if self.model_list:
    #         self._populate_model_combobox()
    #     else:
    #         self.whisperModelComboBox.setVisible(False)

    # def _populate_model_combobox(self):
    #     """
    #     Remplit la ComboBox Whisper avec la liste des modèles et sélectionne le modèle actif.
    #     """
    #     model_list, selected_model = (
    #         self.whisper_model_service.getModelListWithSelection()
    #     )

    #     self.whisperModelComboBox.blockSignals(True)
    #     self.whisperModelComboBox.clear()
    #     self.whisperModelComboBox.addItem(
    #         ParliaStrings.Settings.NO_MODEL_SELECTED, userData=None
    #     )
    #     self.whisperModelComboBox.addItems(model_list)
    #     self.whisperModelComboBox.setVisible(True)

    #     if selected_model in model_list:
    #         index = self.whisperModelComboBox.findText(selected_model)
    #         if index != -1:
    #             self.whisperModelComboBox.setCurrentIndex(index)

    #     self.whisperModelComboBox.blockSignals(False)

    def _updateWhisperStatus(self):
        """
        Met à jour le statut Whisper en fonction de l'état du modèle chargé.
        """
        try:
            text, status_type = self.whisper_model_service.getStatus()
            logger.debug(f"[DEBUG] Statut actuel = {text} / {status_type}")
            if status_type == "ready":
                selected = self.whisper_model_service.getSelectedModel()
                logger.debug(f"[DEBUG] Modèle sélectionné = {selected}")
                if selected:
                    text += f" ({selected})"
            self._set_status(self.whisperStatusValue, text, status_type)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du statut Whisper : {e}")
            self._set_status(self.whisperStatusValue, "Erreur", "error")

    # def _on_model_selected(self, model_name):
    #     """
    #     Gère la sélection d’un modèle dans la liste déroulante.
    #     """
        # self.whisper_model_service.selectModel(
        #     model_name, callback=self._afterModelSelected
        # )

    def _afterModelSelected(self):
        """
        Callback après la sélection ou le chargement d’un modèle.
        """
        # text, status_type = self.whisper_model_service.getStatus()
        # self._set_status(self.whisperStatusValue, text, status_type)
        self._updateWhisperStatus()

        if self.update_record_callback:
            self.update_record_callback()

    def apply_ui_state(self):
        """
        Appliquer l'état de l'interface utilisateur.
        """
        text, status_type = self.ollama_service.get_status()
        self._set_status(self.ollama_status_value, text, status_type)
        self.ollama_start_button.setEnabled(status_type != "ready")

        # Ajout futur
        # text, status_type = self.code_assistant_service.get_status()
        # self._set_status(self.code_status_value, text, status_type)

    def _start_ollama(self):
        """
        Callback pour démarrer ou redémarrer Ollama.
        """
        # Mettre le statut sur "Démarrage en cours..." et désactiver le bouton
        self._set_status(self.ollama_status_value, "Démarrage en cours...", "starting")
        self.ollama_start_button.setEnabled(False)

        # Tenter de démarrer Ollama
        success = self.ollama_service.start()

        # Appliquer l'état de l'interface utilisateur après la tentative
        self.apply_ui_state()

        # Réactiver le bouton si le statut est "Inactif"
        if not success:
            self.ollama_start_button.setEnabled(True)

    def _on_code_model_selected(self, model_name):
        """
        Gère la sélection d'un modèle pour l'assistant de codage.
        """
        logger.info(f"Modèle de l'assistant de codage sélectionné : {model_name}")
        # Simuler une mise à jour de statut
        self._set_status(
            self.code_status_value, f"{model_name}", status_type="ready"
        )

