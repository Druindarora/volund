import subprocess
from typing import Callable, Optional

from src.core.logger_manager import get_logger

logger = get_logger("CodeAssistantService")


class CodeAssistantService:
    def __init__(self):
        self.currentModel = None
        self.availableModels = []
        logger.debug("Initialisation de CodeAssistantService")
        self.refreshModels()

    def _runCommand(self, command: str) -> str:
        """Exécute une commande bash via WSL et renvoie la sortie standard."""
        try:
            logger.debug(f"Exécution commande : {command}")
            result = subprocess.run(
                ["wsl", "-e", "bash", "-c", command],
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=10
            )
            return (result.stdout or "").strip()
        except Exception as e:
            logger.error(f"Erreur commande : {e}")
            return ""

    def refreshModels(self):
        """Met à jour la liste des modèles disponibles via 'ollama list'."""
        logger.debug("Actualisation de la liste des modèles disponibles")
        output = self._runCommand("ollama list")
        models = []
        for line in output.splitlines()[1:]:
            parts = line.strip().split()
            if parts:
                models.append(parts[0])
        self.availableModels = models
        logger.debug(f"Modèles détectés : {models}")

    def getAvailableModels(self) -> list[str]:
        return self.availableModels

    def getCurrentModel(self) -> str | None:
        output = self._runCommand("ollama ps")
        for line in output.splitlines()[1:]:
            parts = line.strip().split()
            if parts:
                logger.debug(f"Modèle chargé détecté : {parts[0]}")
                return parts[0]
        return None

    def isModelLoaded(self) -> bool:
        return self.getCurrentModel() is not None

    def getStatus(self) -> tuple[str, str]:
        model = self.getCurrentModel()
        if model:
            return (f"Chargé : {model}", "ready")
        return ("Non chargé", "neutral")

    def setModel(self, modelName: str) -> bool:
        current = self.getCurrentModel()
        if current == modelName:
            return True
        if modelName not in self.availableModels:
            logger.warning(f"Modèle inconnu : {modelName}")
            return False

        payload = f'{{"model": "{modelName}", "prompt": "ping", "stream": false}}'
        command = f"curl -s http://127.0.0.1:11434/api/generate -d '{payload}'"
        output = self._runCommand(command)
        return bool(output)

    def selectModel(self, modelName: str, on_finished: Optional[Callable[[bool], None]] = None):
        logger.info(f"Sélection du modèle de code : {modelName}")
        success = self.setModel(modelName)
        if on_finished:
            on_finished(success)

    def unloadModel(self) -> bool:
        return False
