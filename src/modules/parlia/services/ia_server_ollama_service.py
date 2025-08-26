# === FICHIER : ia_server_ollama_service.py ===
from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Callable, Optional, cast

import requests

from src.core.logger_manager import get_logger

from .ia_server_types import StatusResponse


class IaServerOllamaService:
    def __init__(
        self,
        baseUrl: str,
        timeout: float = 30.0,
        session: Optional[requests.Session] = None,
        statusProvider: Optional[Callable[[], StatusResponse]] = None,
    ) -> None:
        self.baseUrl: str = baseUrl.rstrip("/")
        self.timeout: float = timeout
        self.session: requests.Session = session or requests.Session()
        self._statusProvider: Optional[Callable[[], StatusResponse]] = statusProvider
        self._executor = ThreadPoolExecutor(max_workers=2)
        self.logger = get_logger("IaServerOllamaService")

    def _getStatus(self) -> StatusResponse:
        if self._statusProvider:
            return self._statusProvider()
        try:
            r = self.session.get(f"{self.baseUrl}/status", timeout=self.timeout)
            r.raise_for_status()
            data: Any = r.json()
            if not isinstance(data, dict):
                raise RuntimeError("Réponse /status inattendue (type non dict)")
            return cast(StatusResponse, data)
        except requests.RequestException as e:
            self.logger.error(f"[Ollama] /status HTTP error: {e}")
            raise RuntimeError(str(e)) from e
        except ValueError as e:
            self.logger.error(f"[Ollama] /status JSON invalide: {e}")
            raise RuntimeError(str(e)) from e

    def getAvailableModels(self) -> list[str]:
        status = self._getStatus()
        return list(status["services"]["ollama"]["models"])

    def getCurrentState(self) -> str:
        status = self._getStatus()
        return str(status["services"]["ollama"]["state"])

    def generate(self, prompt: str, model: Optional[str] = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"prompt": prompt}
        if model:
            payload["model"] = model
        try:
            r = self.session.post(
                f"{self.baseUrl}/ollama/generate",
                json=payload,
                timeout=self.timeout,
            )
            r.raise_for_status()
            data: Any = r.json()
            if not isinstance(data, dict):
                raise RuntimeError("Réponse /ollama/generate inattendue (type non dict)")
            return cast(dict[str, Any], data)
        except requests.RequestException as e:
            self.logger.error(f"[Ollama] generate HTTP error: {e}")
            raise RuntimeError(str(e)) from e
        except ValueError as e:
            self.logger.error(f"[Ollama] generate JSON invalide: {e}")
            raise RuntimeError(str(e)) from e

    def generate_async(
        self, prompt: str, callback: Callable[[dict[str, Any]], None], model: Optional[str] = None
    ) -> None:
        # utilisation de Future de concurrent.futures (pas asyncio)
        future: Future[dict[str, Any]] = self._executor.submit(self.generate, prompt, model)

        def _done(_fut: Future[dict[str, Any]]) -> None:
            try:
                result: dict[str, Any] = _fut.result()
            except Exception as e:
                self.logger.exception(f"[Ollama] generate_async erreur: {e}")
                result = {"error": str(e)}
            try:
                callback(result)
            except Exception as e:
                self.logger.exception(f"[Ollama] callback erreur: {e}")

        future.add_done_callback(_done)

    def cleanup(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)
