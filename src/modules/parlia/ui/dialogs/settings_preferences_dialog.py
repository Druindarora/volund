# preferences_dialog.py

from __future__ import annotations

import logging
from typing import Optional, Callable, Any

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QLabel,
    QVBoxLayout,
)
from qtpy.QtWidgets import QComboBox

from modules.parlia.i18n.parlia_strings import ParliaStrings
from modules.parlia.services import parlia_data

logger = logging.getLogger(__name__)


class PreferencesDialog(QDialog):
    def __init__(self, parent: Any = None, iaServerService: Optional[Any] = None):
        super().__init__(parent)

        # ⚠️ Si l'appelant ne fournit pas IaServerService, on tente de le récupérer sur le parent.
        if iaServerService is None and hasattr(parent, "iaServerService"):
            iaServerService = getattr(parent, "iaServerService")

        # Pas d'exception bloquante : on affichera l'état rouge et on désactivera l'UI si absent.
        if iaServerService is None or not hasattr(iaServerService, "refreshStatus"):
            logger.warning(
                "PreferencesDialog initialisé sans IaServerService valide. "
                "UI en mode dégradé (serveur injoignable). parent=%s",
                type(parent).__name__ if parent else None,
            )
            self.iaServerService = None
        else:
            self.iaServerService = iaServerService

        self.modelSelectedCallback: Optional[Callable[[], None]] = None

        self.setWindowTitle("Préférences")
        self.resize(420, 340)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(20, 20, 20, 20)
        self.mainLayout.setSpacing(14)

        # Label d'état serveur IA
        self.serverStatusLabel = QLabel("…")
        self.serverStatusLabel.setStyleSheet("font-weight: bold;")
        self.mainLayout.addWidget(self.serverStatusLabel)

        # Section Whisper
        whisperTitle = QLabel("🎤 Modèle Whisper")
        whisperTitle.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.mainLayout.addWidget(whisperTitle)

        whisperFixed = QLabel("Modèle actuellement sélectionné :")
        self.mainLayout.addWidget(whisperFixed)

        self.whisperModelComboBox = QComboBox(self)
        self.whisperModelComboBox.setFixedSize(260, 32)
        self.whisperModelComboBox.currentTextChanged.connect(self._onWhisperModelSelected)
        self.mainLayout.addWidget(self.whisperModelComboBox)

        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.HLine)
        sep1.setFrameShadow(QFrame.Shadow.Sunken)
        self.mainLayout.addWidget(sep1)

        # Section Assistant de codage
        codeTitle = QLabel("💻 Assistant de codage")
        codeTitle.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.mainLayout.addWidget(codeTitle)

        codeFixed = QLabel("Modèle actuellement sélectionné :")
        self.mainLayout.addWidget(codeFixed)

        self.codeModelComboBox = QComboBox(self)
        self.codeModelComboBox.setFixedSize(260, 32)
        self.codeModelComboBox.currentTextChanged.connect(self._onCodeModelSelected)
        self.mainLayout.addWidget(self.codeModelComboBox)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setFrameShadow(QFrame.Shadow.Sunken)
        self.mainLayout.addWidget(sep2)

        # Boutons OK / Cancel
        self._buildButtonBox()

        # Chargement initial via IaServerService (ou mode dégradé)
        self._loadServerStatusAndPopulate()

    # --- Initialisation & remplissage ---

    def _loadServerStatusAndPopulate(self) -> None:
        # Si pas de service valide, on force l'état rouge et on désactive.
        if self.iaServerService is None:
            self._setServerReachableUi(False, detail="IaServerService manquant ou invalide.")
            self._disableCombos()
            return

        logger.debug(
            "Ouverture PreferencesDialog: tentative de refreshStatus sur %s (timeout=%s)",
            getattr(self.iaServerService, "baseUrl", "<unknown>"),
            getattr(self.iaServerService, "timeout", "<unknown>"),
        )
        try:
            self.iaServerService.refreshStatus()
            logger.debug("refreshStatus OK. lastUpdated=%s", getattr(self.iaServerService, "lastUpdated", None))

            # Log de synthèse
            try:
                overall = self.iaServerService.getServerStatus()
                whisperAvail = self.iaServerService.getWhisperAvailable()
                ollamaAvail = self.iaServerService.getOllamaAvailable()
                logger.info(
                    "IA server status: overall=%s, whisper.available=%s, ollama.available=%s",
                    overall, whisperAvail, ollamaAvail
                )
            except Exception as e:
                logger.warning("Statut partiel/inattendu reçu depuis /status: %s", e, exc_info=True)

            self._setServerReachableUi(True)
            self._populateWhisperSection()
            self._populateCodeSection()

        except Exception as e:
            # Serveur injoignable : message rouge + désactivation
            logger.exception("Échec refreshStatus dans PreferencesDialog: %s", e)
            self._setServerReachableUi(False, detail=str(e))
            self._disableCombos()

    def _setServerReachableUi(self, reachable: bool, detail: str | None = None) -> None:
        if reachable:
            self.serverStatusLabel.setText("🟢 Connecté au serveur IA — services accessibles.")
            self.serverStatusLabel.setStyleSheet("color: #0a7a1f; font-weight: bold;")
            self.serverStatusLabel.setToolTip("")
        else:
            self.serverStatusLabel.setText("🔴 Serveur IA injoignable — veuillez le redémarrer manuellement.")
            self.serverStatusLabel.setStyleSheet("color: #a40000; font-weight: bold;")
            if detail:
                self.serverStatusLabel.setToolTip(detail)

    def _disableCombos(self) -> None:
        self.whisperModelComboBox.blockSignals(True)
        self.whisperModelComboBox.clear()
        self.whisperModelComboBox.addItem("Modèle à choisir")
        self.whisperModelComboBox.setEnabled(False)
        self.whisperModelComboBox.blockSignals(False)

        self.codeModelComboBox.blockSignals(True)
        self.codeModelComboBox.clear()
        self.codeModelComboBox.addItem("Modèle à choisir")
        self.codeModelComboBox.setEnabled(False)
        self.codeModelComboBox.blockSignals(False)

    def _populateWhisperSection(self) -> None:
        # Remplir avec liste + sélectionner via persistance locale (GetWhisperModel) sinon modèle courant serveur
        self.whisperModelComboBox.blockSignals(True)
        self.whisperModelComboBox.clear()
        self.whisperModelComboBox.addItem("Modèle à choisir")

        isAvailable = False
        try:
            isAvailable = bool(self.iaServerService.getWhisperAvailable())
        except Exception as e:
            logger.warning("getWhisperAvailable a échoué: %s", e, exc_info=True)
            isAvailable = False

        if isAvailable:
            try:
                models = self.iaServerService.getWhisperModelList() or []
                logger.debug("Whisper models: %s", models)
            except Exception as e:
                logger.warning("getWhisperModelList a échoué: %s", e, exc_info=True)
                models = []

            if models:
                self.whisperModelComboBox.addItems(models)

            self.whisperModelComboBox.setEnabled(True)

            # --- Sélection : priorité au modèle persistant localement ---
            selectedIdx = -1
            try:
                savedModel = parlia_data.get_whisper_model()  # persistance locale
                logger.debug("Whisper model (persisted): %s", savedModel)
                if savedModel:
                    selectedIdx = self.whisperModelComboBox.findText(savedModel)
            except Exception as e:
                logger.warning("get_whisper_model a échoué: %s", e, exc_info=True)

            # Si pas trouvé localement, fallback au modèle courant du serveur
            if selectedIdx == -1:
                try:
                    currentModel = self.iaServerService.getCurrentWhisperModel()
                    logger.debug("Whisper current model (server): %s", currentModel)
                    if currentModel:
                        selectedIdx = self.whisperModelComboBox.findText(currentModel)
                except Exception as e:
                    logger.warning("getCurrentWhisperModel a échoué: %s", e, exc_info=True)

            if selectedIdx != -1:
                self.whisperModelComboBox.setCurrentIndex(selectedIdx)
        else:
            self.whisperModelComboBox.setEnabled(False)

        self.whisperModelComboBox.blockSignals(False)

    def _populateCodeSection(self) -> None:
        self.codeModelComboBox.blockSignals(True)
        self.codeModelComboBox.clear()
        self.codeModelComboBox.addItem("Modèle à choisir")

        isAvailable = False
        try:
            isAvailable = bool(self.iaServerService.getOllamaAvailable())
        except Exception as e:
            logger.warning("getOllamaAvailable a échoué: %s", e, exc_info=True)
            isAvailable = False

        if isAvailable:
            try:
                models = self.iaServerService.getOllamaModelList() or []
                logger.debug("Ollama models: %s", models)
            except Exception as e:
                logger.warning("getOllamaModelList a échoué: %s", e, exc_info=True)
                models = []
            if models:
                self.codeModelComboBox.addItems(models)
            self.codeModelComboBox.setEnabled(True)
            selected = parlia_data.get_code_model()
            logger.debug("Code model (persisted): %s", selected)
            if selected:
                idx = self.codeModelComboBox.findText(selected)
                if idx != -1:
                    self.codeModelComboBox.setCurrentIndex(idx)
        else:
            self.codeModelComboBox.setEnabled(False)

        self.codeModelComboBox.blockSignals(False)

    # --- Actions utilisateur ---

    def _onWhisperModelSelected(self, modelName: str) -> None:
        if not modelName or modelName == "Modèle à choisir":
            return
        try:
            # Étape 1 : sauvegarde locale
            parlia_data.set_whisper_model(modelName)
            logger.info("Whisper model sélectionné et persisté: %s", modelName)

            # Étape 2 : envoi au serveur
            if self.iaServerService:
                self.iaServerService.selectWhisperModel(modelName)
                logger.info("Whisper model envoyé au serveur IA: %s", modelName)
            else:
                logger.warning("Pas de iaServerService disponible pour envoyer le modèle au serveur.")
        except Exception as e:
            logger.error("Erreur lors de la sélection du modèle Whisper: %s", e, exc_info=True)

        # Étape 3 : callback UI
        self._notifyModelSelected()


    def _onCodeModelSelected(self, modelName: str) -> None:
        if not modelName or modelName == "Modèle à choisir":
            return
        parlia_data.set_code_model(modelName)
        logger.info("Code model sélectionné et persisté: %s", modelName)
        self._notifyModelSelected()

    # --- API publique ---

    def setModelSelectedCallback(self, callback: Callable[[], None]) -> None:
        self.modelSelectedCallback = callback

    # --- Interne ---

    def _notifyModelSelected(self) -> None:
        if self.modelSelectedCallback:
            self.modelSelectedCallback()

    def _buildButtonBox(self) -> None:
        buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        buttonBox.setCenterButtons(True)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.mainLayout.addWidget(buttonBox)
