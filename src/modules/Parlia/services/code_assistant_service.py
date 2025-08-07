import subprocess
from typing import Callable, Optional


class CodeAssistantService:
    def __init__(self):
        self.currentModel = None
        self.availableModels = []
        self.refreshModels()

    def _runCommand(self, command: str) -> str:
        """Exécute une commande bash via WSL et renvoie la sortie standard."""
        try:
            result = subprocess.run(
                ["wsl", "-e", "bash", "-c", command],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip()
        except Exception as e:
            print(f"[CodeAssistantService] Erreur commande : {e}")
            return ""

    def refreshModels(self):
        """Met à jour la liste des modèles disponibles via 'ollama list'."""
        output = self._runCommand("ollama list")
        models = []
        for line in output.splitlines()[1:]:  # Ignore l'entête
            parts = line.strip().split()
            if parts:
                models.append(parts[0])
        self.availableModels = models

    def getAvailableModels(self) -> list[str]:
        """Retourne la liste des modèles disponibles."""
        return self.availableModels

    def getCurrentModel(self) -> str | None:
        """Retourne le nom du modèle chargé actuellement via 'ollama ps'."""
        output = self._runCommand("ollama ps")
        for line in output.splitlines()[1:]:  # Ignore l'entête
            parts = line.strip().split()
            if parts:
                return parts[0]
        return None

    def isModelLoaded(self) -> bool:
        """Indique si un modèle est actuellement chargé."""
        return self.getCurrentModel() is not None

    def getStatus(self) -> str:
        """Retourne un label de statut : 'Non chargé' ou 'Chargé : <modèle>'."""
        model = self.getCurrentModel()
        if model:
            return f"Chargé : {model}"
        return "Non chargé"

    def setModel(self, modelName: str) -> bool:
        """Charge un modèle s'il n'est pas déjà actif. Utilise un ping silencieux."""
        current = self.getCurrentModel()
        if current == modelName:
            return True  # Déjà actif

        if modelName not in self.availableModels:
            print(f"[CodeAssistantService] Modèle inconnu : {modelName}")
            return False

        # Tentative de chargement via un prompt minimal
        payload = (
            f'{{"model": "{modelName}", "prompt": "ping", "stream": false}}'
        )
        command = f"curl -s http://127.0.0.1:11434/api/generate -d '{payload}'"
        output = self._runCommand(command)
        return bool(output)

    def selectModel(self, modelName: str, on_finished: Optional[Callable[[bool], None]] = None):
        """
        Charge le modèle de codage sélectionné et appelle un callback avec True/False selon le succès.
        """
        success = self.setModel(modelName)
        if on_finished:
            on_finished(success)


    def unloadModel(self) -> bool:
        """Tentative d'arrêt du modèle actif (non supporté directement par Ollama)."""
        # Ollama ne propose pas d'arrêt explicite d'un modèle
        # Mais on peut contourner en tuant le processus si besoin, ou ignorer
        # À implémenter plus tard si vraiment nécessaire
        return False
