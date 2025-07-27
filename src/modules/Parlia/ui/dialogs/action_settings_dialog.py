# === FICHIER : action_settings_dialog.py (ex-prompt_editor_dialog.py) ===
# 🔍 Audit final d'un dialog simple destiné à éditer les prompts personnalisés
# --------------------------------------------------
# ✅ Propre, lisible, efficace
# 🟡 Va évoluer pour intégrer d'autres réglages liés aux actions personnalisées
# --------------------------------------------------

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
)

from modules.parlia.services.parlia_data import (
    PROMPT_DEFINITIONS,
    get_prompt,
    get_prompt_label,
    set_prompt,
)


class ActionSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Paramètres des actions personnalisées")
        self.setModal(True)
        self.inputs = {}  # key -> QPlainTextEdit

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()

        for key in PROMPT_DEFINITIONS:
            label = QLabel(get_prompt_label(key))
            label.setStyleSheet("font-weight: bold;")
            layout.addWidget(label)

            field = QPlainTextEdit(get_prompt(key))
            self.inputs[key] = field
            layout.addWidget(field)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._save_prompts)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def _save_prompts(self):
        for key, field in self.inputs.items():
            content = field.toPlainText().strip()
            set_prompt(key, content)
        self.accept()
