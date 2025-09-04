# ui/dialogs/create_module_dialog.py

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.modules.parlia.services.macro.module_creator_service import createModule


class CreateModuleDialog(QDialog):
    """Boîte de dialogue pour créer un nouveau module."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Create New Module")
        self.setModal(True)
        self.setMinimumWidth(420)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # --- Nom du module (obligatoire)
        nameRow = QHBoxLayout()
        nameLabel = QLabel("Module name:", self)
        self.moduleNameInput = QLineEdit(self)
        self.moduleNameInput.setPlaceholderText("ex: parlia")
        nameRow.addWidget(nameLabel)
        nameRow.addWidget(self.moduleNameInput)
        root.addLayout(nameRow)

        # --- Description (optionnelle)
        descLabel = QLabel("Description (optional):", self)
        self.descriptionInput = QTextEdit(self)
        self.descriptionInput.setPlaceholderText("Short description…")
        self.descriptionInput.setAcceptRichText(False)
        self.descriptionInput.setFixedHeight(90)
        root.addWidget(descLabel)
        root.addWidget(self.descriptionInput)

        # --- Cible mobile
        self.mobileCheckbox = QCheckBox("Mobile support", self)
        self.mobileCheckbox.setChecked(False)
        root.addWidget(self.mobileCheckbox)

        # --- Boutons
        btnRow = QHBoxLayout()
        btnRow.addStretch(1)
        self.createButton = QPushButton("Créer", self)
        self.cancelButton = QPushButton("Annuler", self)
        self.createButton.clicked.connect(self._onCreateClicked)
        self.cancelButton.clicked.connect(self._onCancelClicked)
        btnRow.addWidget(self.createButton)
        btnRow.addWidget(self.cancelButton)
        root.addLayout(btnRow)

    @Slot()
    def _onCreateClicked(self) -> None:
        """Validation et appel du service de création."""
        name = self.moduleNameInput.text().strip()
        if not name:
            QMessageBox.critical(self, "Erreur", "Le nom du module est obligatoire.")
            return

        description = self.descriptionInput.toPlainText().strip()
        mobile = bool(self.mobileCheckbox.isChecked())

        ok = createModule(name=name, description=description, mobile=mobile)
        if ok:
            QMessageBox.information(self, "Succès", f"Module '{name}' créé avec succès.")
            self.accept()
        else:
            QMessageBox.warning(
                self, "Échec", f"Impossible de créer le module '{name}' (existe déjà ou erreur)."
            )

    @Slot()
    def _onCancelClicked(self) -> None:
        """Ferme le dialogue sans rien faire."""
        self.reject()
