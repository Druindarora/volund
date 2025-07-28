from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout


class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Configuration de la fenêtre
        self.setWindowTitle("Préférences")
        self.resize(400, 300)  # Taille par défaut

        # Layout principal
        layout = QVBoxLayout(self)

        # Message temporaire
        message = QLabel("Fenêtre Préférences (en cours de construction)", self)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message)

        # Boutons OK / Annuler
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)
