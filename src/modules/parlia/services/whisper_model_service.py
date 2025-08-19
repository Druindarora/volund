import os

from modules.parlia.core.whisper_manager import unload_model
from modules.parlia.services.parlia_data import (
    get_model_folder_path,
    get_model_name,
    set_model_name,
)
from modules.parlia.services.whisper_service import whisper_service


class WhisperModelService:
    def __init__(self):
        self.modelFolder = get_model_folder_path()

    def listAvailableModels(self) -> list[str]:
        """
        Retourne la liste des modèles valides (.pt, .bin) dans le dossier utilisateur.
        """
        if not self.modelFolder or not os.path.isdir(self.modelFolder):
            return []

        return [f for f in os.listdir(self.modelFolder) if f.endswith((".pt", ".bin"))]

    def getSelectedModel(self) -> str:
        """
        Retourne le modèle sélectionné depuis parlia_data.
        """
        return get_model_name()

    def setSelectedModel(self, modelName: str):
        """
        Sauvegarde le modèle choisi dans parlia_data.
        """
        set_model_name(modelName)

    def loadModel(self, modelName: str, callback=None):
        """
        Charge le modèle via whisper_service.load_model_async.
        """
        whisper_service.load_model_async(modelName, on_finished=callback)

    def unloadModel(self):
        """
        Décharge le modèle via whisper_manager.unload_model.
        """
        unload_model()

    def is_model_loaded(self) -> bool:
        """
        Vérifie si un modèle est actuellement chargé via whisper_manager.
        """
        from modules.parlia.core.whisper_manager import is_model_loaded

        return is_model_loaded()

    def getStatus(self) -> tuple[str, str]:
        """
        Retourne le statut actuel du modèle Whisper sous forme de texte et de type.
        """
        from modules.parlia.core.whisper_manager import is_model_loaded

        try:
            if is_model_loaded():
                return ("Prêt", "ready")

            selected_model = self.getSelectedModel()
            if selected_model:
                return ("Non chargé", "neutral")

            return ("Inactif", "neutral")
        except Exception as e:
            from src.core.logger_manager import get_logger

            logger = get_logger("WhisperModelService")
            logger.error(f"Erreur lors de la vérification du statut : {e}")
            return ("Erreur", "error")

    def selectModel(self, modelName: str, callback=None):
        """
        Gère la sélection d’un modèle Whisper.
        """
        from modules.parlia.i18n.parlia_strings import ParliaStrings

        if modelName == ParliaStrings.Settings.NO_MODEL_SELECTED:
            self.unloadModel()
        else:
            self.setSelectedModel(modelName)
            self.loadModel(modelName, callback=callback)

    def getModelListWithSelection(self) -> tuple[list[str], str]:
        """
        Retourne la liste des modèles disponibles et le modèle actuellement sélectionné.
        """
        model_list = self.listAvailableModels()
        selected_model = self.getSelectedModel()
        return model_list, selected_model

    def initializeModel(self, callback=None):
        """
        Initialise le modèle sauvegardé au démarrage en le chargeant si nécessaire.
        """
        selected_model = self.getSelectedModel()
        if selected_model:
            self.loadModel(selected_model, callback=callback)
