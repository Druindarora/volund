from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,  # Import pour la ligne de séparation
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from modules.parlia.i18n.parlia_strings import ParliaStrings
from modules.parlia.services.parlia_data import (
    get_model_folder_path,
    set_model_folder_path,
)


class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Configuration de la fenêtre
        self.setWindowTitle("Préférences")
        self.resize(400, 300)  # Taille par défaut

        # Layout principal avec marges
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)  # Ajout de marges autour du texte
        layout.setSpacing(15)  # Espacement global entre les widgets

        # Section 1 : Modèle Whisper
        whisper_title = QLabel("🎤 Modèle Whisper")
        whisper_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(whisper_title)

        whisper_layout = QHBoxLayout()
        self.select_whisper_button = QPushButton("Choisir dossier", self)
        self.select_whisper_button.clicked.connect(self._select_whisper_folder)
        whisper_layout.addWidget(self.select_whisper_button)

        self.whisperPathLabel = QLabel(self)
        self._update_whisper_path_label()
        whisper_layout.addWidget(self.whisperPathLabel)

        layout.addLayout(whisper_layout)

        # Ligne de séparation
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Section 2 : Assistant de codage
        code_title = QLabel("💻 Assistant de codage")
        code_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(code_title)

        code_layout = QHBoxLayout()
        self.select_code_button = QPushButton("Choisir dossier", self)
        self.select_code_button.clicked.connect(self._select_code_folder)
        code_layout.addWidget(self.select_code_button)

        self.codePathLabel = QLabel("(aucun dossier sélectionné)", self)
        code_layout.addWidget(self.codePathLabel)

        layout.addLayout(code_layout)

        # Ligne de séparation avant les boutons OK/Annuler
        final_separator = QFrame()
        final_separator.setFrameShape(QFrame.Shape.HLine)
        final_separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(final_separator)

        # Boutons OK / Annuler centrés
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        button_box.setCenterButtons(True)  # Centrer les boutons
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def _select_whisper_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, ParliaStrings.Settings.CHOOSE_FOLDER
        )
        if folder:
            set_model_folder_path(folder)
            self._update_whisper_path_label()

    def _update_whisper_path_label(self):
        folder = get_model_folder_path()
        if folder:
            self.whisperPathLabel.setText(
                ParliaStrings.Settings.CURRENT_FOLDER.format(folder=folder)
            )
        else:
            self.whisperPathLabel.setText(ParliaStrings.Settings.NO_MODEL_SELECTED)

    def _select_code_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Choisir un dossier pour l'assistant de codage"
        )
        if folder:
            self.codePathLabel.setText(folder)
