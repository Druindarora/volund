import time

import requests

from src.core.logger_manager import get_logger
from src.modules.parlia.core.check_olama import (
    checkWslInstalled,
    isOllamaRunning,
    startOllamaService,
)

logger = get_logger("OllamaService")


class OllamaService:
    def __init__(self, host="localhost", port=11434, binaryPath="ollama"):
        self.host = host
        self.port = port
        self.binaryPath = binaryPath
        self.ollamaActive = False
        self.ollamaProcess = None

    def get_status(self) -> tuple[str, str]:
        """
        Retourne le statut d'Ollama après vérification réelle du serveur.
        """
        self.check_server()
        return ("Actif", "ready") if self.ollamaActive else ("Inactif", "error")

    def check_server(self) -> bool:
        """
        Vérifie si le serveur Ollama est actif.
        """
        try:
            url = f"http://{self.host}:{self.port}/api/version"
            response = requests.get(url, timeout=5)
            self.ollamaActive = response.status_code == 200
            if self.ollamaActive:
                logger.info(f"[Ollama] Serveur disponible à {url}")
            else:
                logger.warning(
                    f"[Ollama] Serveur indisponible, code HTTP : {response.status_code}"
                )
        except requests.RequestException as e:
            self.ollamaActive = False
            logger.error(f"[Ollama] Erreur check_server : {e}")
        return self.ollamaActive

    def start(self, timeout=10) -> bool:
        """
        Démarre Ollama via WSL et vérifie le serveur.
        """
        if not checkWslInstalled():
            logger.error("WSL non disponible.")
            return False

        if isOllamaRunning():
            logger.info("OLLAMA déjà en cours.")
            return self.check_server()

        if startOllamaService():
            logger.info("Tentative de démarrage d'OLAMA via WSL...")
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.check_server():
                    logger.info("OLAMA démarré avec succès.")
                    return True
                time.sleep(1)

            logger.error("Timeout lors du démarrage d'OLAMA via WSL.")
        else:
            logger.error("Impossible de démarrer OLAMA via WSL.")

        return False

    def stop(self) -> bool:
        """
        Arrête le processus Ollama si actif.
        """
        if self.ollamaProcess is None:
            logger.warning("[Ollama] Aucun processus à arrêter.")
            return False

        try:
            self.ollamaProcess.terminate()
            self.ollamaProcess.wait()
            logger.info("[Ollama] Serveur arrêté avec succès.")
        except Exception as e:
            logger.error(f"[Ollama] Erreur lors de l'arrêt : {e}")
            return False
        finally:
            self.ollamaActive = False
            self.ollamaProcess = None

        return True
