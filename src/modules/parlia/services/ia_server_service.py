# ia_server_service.py

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional, TypedDict, cast

import requests

logger = logging.getLogger(__name__)


# --- Schéma typé de la réponse /status ---


class WhisperModels(TypedDict):
    downloaded: list[str]
    current: str


class WhisperService(TypedDict):
    available: bool
    state: str
    models: WhisperModels


class OllamaService(TypedDict):
    available: bool
    state: str
    models: list[str]


class ServicesDict(TypedDict):
    whisper: WhisperService
    ollama: OllamaService


class StatusDict(TypedDict):
    overall: str
    services: ServicesDict


class IaServerService:
    """Service centralisant l'état et les modèles d'un serveur IA distant."""

    def __init__(
        self, baseUrl: str, timeout: float = 5.0, session: Optional[requests.Session] = None
    ) -> None:
        self.baseUrl: str = baseUrl.rstrip("/")
        self.timeout: float = timeout
        self.session: requests.Session = session or requests.Session()
        self.status: Optional[StatusDict] = None
        self.lastUpdated: Optional[datetime] = None

    def refreshStatus(self) -> None:
        """Effectue un GET /status et met à jour le cache local."""
        url = f"{self.baseUrl}/status"
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            # On caste vers le schéma attendu (validation légère côté client)
            self.status = cast(StatusDict, data)
            self.lastUpdated = datetime.utcnow()
            logger.debug("Statut serveur IA mis à jour à %s", self.lastUpdated.isoformat())
        except requests.RequestException as exc:
            logger.error("Échec de récupération du statut IA (%s): %s", url, exc, exc_info=True)
            raise RuntimeError(f"Unable to refresh IA server status from {url}") from exc
        except ValueError as exc:
            logger.error("Réponse /status invalide (JSON): %s", exc, exc_info=True)
            raise RuntimeError("Invalid JSON received from IA server /status") from exc

    def selectWhisperModel(self, modelName: str) -> dict[str, Any]:
        """POST /whisper/select avec {name:modelName}.
        Retourne la réponse JSON du serveur (state, current, requested)."""
        url = f"{self.baseUrl}/whisper/select"
        payload = {"name": modelName}  # important: clé "name" demandée
        logger.debug("Requête POST %s avec modèle Whisper='%s'", url, modelName)
        try:
            resp = self.session.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout,
            )
            # On ne fait pas raise_for_status pour laisser l'appelant gérer 423 Locked
            return cast(dict[str, Any], resp.json())
        except requests.RequestException as exc:
            logger.error("Échec POST sélection Whisper (%s): %s", url, exc, exc_info=True)
            raise RuntimeError(f"Unable to select Whisper model '{modelName}' on {url}") from exc
        except ValueError as exc:
            logger.error("Réponse /whisper/select invalide (JSON): %s", exc, exc_info=True)
            raise RuntimeError("Invalid JSON received from IA server /whisper/select") from exc

    # --- Accès aux données en cache ---

    def getServerStatus(self) -> str:
        status = self._ensureLoaded()
        return status["overall"]

    def getWhisperAvailable(self) -> bool:
        status = self._ensureLoaded()
        return status["services"]["whisper"]["available"]

    def getWhisperState(self) -> str:
        status = self._ensureLoaded()
        return status["services"]["whisper"]["state"]

    def getWhisperModelList(self) -> list[str]:
        status = self._ensureLoaded()
        return status["services"]["whisper"]["models"]["downloaded"]

    def getCurrentWhisperModel(self) -> str:
        status = self._ensureLoaded()
        return status["services"]["whisper"]["models"]["current"]

    def getOllamaAvailable(self) -> bool:
        status = self._ensureLoaded()
        return status["services"]["ollama"]["available"]

    def getOllamaState(self) -> str:
        status = self._ensureLoaded()
        return status["services"]["ollama"]["state"]

    def getOllamaModelList(self) -> list[str]:
        status = self._ensureLoaded()
        return status["services"]["ollama"]["models"]

    # --- Outils internes ---

    def _ensureLoaded(self) -> StatusDict:
        # Vérifie que le cache est disponible et retourne le dict typé
        if self.status is None:
            raise RuntimeError("Status not loaded. Call refreshStatus() first.")
        return self.status
