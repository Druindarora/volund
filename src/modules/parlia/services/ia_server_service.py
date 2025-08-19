# ia_server_service.py

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class IaServerService:
    """Service centralisant l'état et les modèles d'un serveur IA distant."""

    def __init__(self, baseUrl: str, timeout: float = 5.0, session: Optional[requests.Session] = None) -> None:
        self.baseUrl = baseUrl.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()
        self.status: Optional[dict[str, Any]] = None
        self.lastUpdated: Optional[datetime] = None

    def refreshStatus(self) -> None:
        """Effectue un GET /status et met à jour le cache local."""
        url = f"{self.baseUrl}/status"
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            self.status = resp.json()
            self.lastUpdated = datetime.utcnow()
            logger.debug("Statut serveur IA mis à jour à %s", self.lastUpdated.isoformat())
        except requests.RequestException as exc:
            logger.error("Échec de récupération du statut IA (%s): %s", url, exc, exc_info=True)
            raise RuntimeError(f"Unable to refresh IA server status from {url}") from exc
        except ValueError as exc:
            logger.error("Réponse /status invalide (JSON): %s", exc, exc_info=True)
            raise RuntimeError("Invalid JSON received from IA server /status") from exc

    def selectWhisperModel(self, modelName: str) -> None:
        """Demande au serveur IA de sélectionner un modèle Whisper."""
        url = f"{self.baseUrl}/whisper/select"
        payload = {"model": modelName}
        logger.debug("Requête POST %s avec modèle Whisper='%s'", url, modelName)
        try:
            resp = self.session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout,
            )
            resp.raise_for_status()
            logger.info("Modèle Whisper sélectionné avec succès : %s", modelName)
            # Optionnel : rafraîchir le cache après sélection
            try:
                self.refreshStatus()
            except Exception as e:
                logger.warning("Impossible de rafraîchir le statut après sélection modèle: %s", e)
        except requests.RequestException as exc:
            logger.error("Échec POST sélection Whisper (%s): %s", url, exc, exc_info=True)
            raise RuntimeError(f"Unable to select Whisper model '{modelName}' on {url}") from exc

    # --- Accès aux données en cache ---

    def getServerStatus(self) -> str:
        return self._get(["overall"])

    def getWhisperAvailable(self) -> bool:
        return self._get(["services", "whisper", "available"])

    def getWhisperState(self) -> str:
        return self._get(["services", "whisper", "state"])

    def getWhisperModelList(self) -> list[str]:
        return self._get(["services", "whisper", "models", "downloaded"])

    def getCurrentWhisperModel(self) -> str:
        return self._get(["services", "whisper", "models", "current"])

    def getOllamaAvailable(self) -> bool:
        return self._get(["services", "ollama", "available"])

    def getOllamaState(self) -> str:
        return self._get(["services", "ollama", "state"])

    def getOllamaModelList(self) -> list[str]:
        return self._get(["services", "ollama", "models"])

    # --- Outils internes ---

    def _ensureLoaded(self) -> None:
        if self.status is None:
            raise RuntimeError("Status not loaded. Call refreshStatus() first.")

    def _get(self, path: list[str]) -> Any:
        self._ensureLoaded()
        node: Any = self.status  # type: ignore[assignment]
        try:
            for key in path:
                node = node[key]  # type: ignore[index]
            return node
        except (KeyError, TypeError) as exc:
            logger.error("Clé manquante dans le statut pour le chemin %s", " -> ".join(path), exc_info=True)
            raise RuntimeError(f"Missing expected key in status at path: {'/'.join(path)}") from exc
