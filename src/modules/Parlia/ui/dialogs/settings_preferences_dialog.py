from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)
from qtpy.QtWidgets import QComboBox

from modules.parlia.i18n.parlia_strings import ParliaStrings
from modules.parlia.services.code_assistant_service import CodeAssistantService
from modules.parlia.services.parlia_data import (
    get_model_folder_path,
    set_model_folder_path,
)
from modules.parlia.services.whisper_model_service import WhisperModelService


class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Préférences")
        self.resize(400, 300)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)
        self.mainLayout.setSpacing(15)

        self.build_whisper_section()
        self.build_code_assistant_section()
        self.build_button_box()

    def build_whisper_section(self):
        whisper_title = QLabel("🎤 Modèle Whisper")
        whisper_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.mainLayout.addWidget(whisper_title)

        whisper_layout = QHBoxLayout()
        self.select_whisper_button = QPushButton("Choisir dossier", self)
        self.select_whisper_button.clicked.connect(self._select_whisper_folder)
        whisper_layout.addWidget(self.select_whisper_button)

        self.whisperPathLabel = QLabel(self)
        self._update_whisper_path_label()
        whisper_layout.addWidget(self.whisperPathLabel)

        self.mainLayout.addLayout(whisper_layout)

        self.whisper_model_combobox = QComboBox(self)
        self.whisper_model_combobox.setFixedSize(220, 32)
        self.whisper_model_combobox.addItem("Aucun modèle disponible")  # provisoire
        self.whisper_model_combobox.currentTextChanged.connect(self._on_whisper_model_selected)
        self.mainLayout.addWidget(self.whisper_model_combobox)

        self._update_model_list()

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.mainLayout.addWidget(separator)

    def build_code_assistant_section(self):
        code_title = QLabel("💻 Assistant de codage")
        code_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.mainLayout.addWidget(code_title)

        # code_layout = QHBoxLayout()
        # self.select_code_button = QPushButton("Choisir dossier", self)
        # self.select_code_button.clicked.connect(self._select_code_folder)
        # code_layout.addWidget(self.select_code_button)

        # self.codePathLabel = QLabel("(aucun dossier sélectionné)", self)
        # code_layout.addWidget(self.codePathLabel)

        # self.mainLayout.addLayout(code_layout)

        self.code_model_combobox = QComboBox(self)
        self.code_model_combobox.setFixedSize(220, 32)
        # self.code_model_combobox.addItem("Aucun modèle disponible")  # provisoire
        self.codeAssistantService = CodeAssistantService()
        self._update_code_model_list()

        self.code_model_combobox.currentTextChanged.connect(self._on_code_model_selected)
        self.mainLayout.addWidget(self.code_model_combobox)


        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        self.mainLayout.addWidget(separator)

    def _update_code_model_list(self):
        model_list = self.codeAssistantService.getAvailableModels()
        self._populate_code_model_combobox(model_list)

    def _populate_code_model_combobox(self, model_list):
        self.code_model_combobox.blockSignals(True)
        self.code_model_combobox.clear()

        self.code_model_combobox.addItem("Aucun modèle sélectionné")

        if model_list:
            self.code_model_combobox.addItems(model_list)
            self.code_model_combobox.setEnabled(True)
        else:
            self.code_model_combobox.setEnabled(False)

        self.code_model_combobox.setCurrentIndex(0)
        self.code_model_combobox.blockSignals(False)


    def build_button_box(self):
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        button_box.setCenterButtons(True)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self.mainLayout.addWidget(button_box)

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

    # def _select_code_folder(self):
    #     folder = QFileDialog.getExistingDirectory(
    #         self, "Choisir un dossier pour l'assistant de codage"
    #     )
    #     if folder:
    #         self.codePathLabel.setText(folder)

    def _on_whisper_model_selected(self, model_name: str):
        if model_name and model_name != "Aucun modèle disponible":
            WhisperModelService().selectModel(model_name, callback=self._notify_model_selected)

    def set_model_selected_callback(self, callback):
        self._model_selected_callback = callback

    def _notify_model_selected(self):
        if hasattr(self, "_model_selected_callback"):
            self._model_selected_callback()

    def _on_code_model_selected(self, model_name: str):
        if model_name and model_name != "Aucun modèle disponible":
            self.codeAssistantService = CodeAssistantService()
            self.codeAssistantService.selectModel(model_name)

    def _update_model_list(self):
        model_list, selected_model = WhisperModelService().getModelListWithSelection()
        self._populate_model_combobox(model_list, selected_model)

    def _populate_model_combobox(self, model_list, selected_model):
        self.whisper_model_combobox.blockSignals(True)
        self.whisper_model_combobox.clear()

        if not model_list:
            self.whisper_model_combobox.addItem("Aucun modèle disponible")
            self.whisper_model_combobox.setEnabled(False)
        else:
            self.whisper_model_combobox.addItem(ParliaStrings.Settings.NO_MODEL_SELECTED)
            self.whisper_model_combobox.addItems(model_list)
            self.whisper_model_combobox.setEnabled(True)

            if selected_model in model_list:
                index = self.whisper_model_combobox.findText(selected_model)
                if index != -1:
                    self.whisper_model_combobox.setCurrentIndex(index)

        self.whisper_model_combobox.blockSignals(False)
