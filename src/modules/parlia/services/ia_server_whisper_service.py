# === FICHIER : ia_server_whisper_service.py ===
from __future__ import annotations

import os
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Callable, Optional, cast

import requests

from src.core.logger_manager import get_logger


class IaServerWhisperService:
    def __init__(
        self,
        baseUrl: str,
        timeout: float = 30.0,
        session: Optional[requests.Session] = None,
        statusProvider: Optional[Callable[[], dict[str, Any]]] = None,
    ) -> None:
        self.baseUrl: str = baseUrl.rstrip("/")
        self.timeout: float = timeout
        self.session: requests.Session = session or requests.Session()
        self._statusProvider: Optional[Callable[[], dict[str, Any]]] = statusProvider
        self._executor = ThreadPoolExecutor(max_workers=2)
        self.logger = get_logger("IaServerWhisperService")

    def _getStatus(self) -> dict[str, Any]:
        if self._statusProvider:
            return self._statusProvider()
        try:
            r = self.session.get(f"{self.baseUrl}/status", timeout=self.timeout)
            r.raise_for_status()
            data: Any = r.json()
            if not isinstance(data, dict):
                raise RuntimeError("Réponse /status inattendue (type non dict)")
            return cast(dict[str, Any], data)
        except requests.RequestException as e:
            self.logger.error(f"[Whisper] /status HTTP error: {e}")
            raise RuntimeError(str(e)) from e
        except ValueError as e:
            self.logger.error(f"[Whisper] /status JSON invalide: {e}")
            raise RuntimeError(str(e)) from e

    def selectModel(self, modelName: str) -> dict[str, Any]:
        try:
            r = self.session.post(
                f"{self.baseUrl}/whisper/select",
                json={"name": modelName},
                timeout=self.timeout,
            )
            r.raise_for_status()
            data: Any = r.json()
            if not isinstance(data, dict):
                raise RuntimeError("Réponse /whisper/select inattendue (type non dict)")
            return cast(dict[str, Any], data)
        except requests.RequestException as e:
            self.logger.error(f"[Whisper] selectModel HTTP error: {e}")
            raise RuntimeError(str(e)) from e
        except ValueError as e:
            self.logger.error(f"[Whisper] selectModel JSON invalide: {e}")
            raise RuntimeError(str(e)) from e

    def getAvailableModels(self) -> list[str]:
        status = self._getStatus()
        return list(status.get("whisper", {}).get("models", []))

    def getCurrentModel(self) -> str:
        status = self._getStatus()
        return str(status.get("whisper", {}).get("current", ""))

    def transcribe(self, filePath: str) -> dict[str, Any]:
        if not os.path.exists(filePath):
            msg = f"Fichier audio introuvable: {filePath}"
            self.logger.error(f"[Whisper] {msg}")
            raise RuntimeError(msg)
        try:
            with open(filePath, "rb") as f:
                files = {"file": (os.path.basename(filePath), f, "audio/wav")}
                r = self.session.post(
                    f"{self.baseUrl}/whisper/transcribe",
                    files=files,
                    timeout=self.timeout,
                )
            r.raise_for_status()
            data: Any = r.json()
            if not isinstance(data, dict):
                raise RuntimeError("Réponse /whisper/transcribe inattendue (type non dict)")
            return cast(dict[str, Any], data)
        except requests.RequestException as e:
            self.logger.error(f"[Whisper] transcribe HTTP error: {e}")
            raise RuntimeError(str(e)) from e
        except ValueError as e:
            self.logger.error(f"[Whisper] transcribe JSON invalide: {e}")
            raise RuntimeError(str(e)) from e

    def transcribe_async(self, filePath: str, callback: Callable[[dict[str, Any]], None]) -> None:
        future: Future[dict[str, Any]] = self._executor.submit(self.transcribe, filePath)

        def _done(_fut: Future[dict[str, Any]]) -> None:
            try:
                result: dict[str, Any] = _fut.result()
            except Exception as e:
                self.logger.error(f"[Whisper] transcribe_async erreur: {e}")
                result = {"error": str(e)}
            try:
                callback(result)
            except Exception as e:
                self.logger.error(f"[Whisper] callback erreur: {e}")

        future.add_done_callback(_done)

    def cleanup(self) -> None:
        self._executor.shutdown(wait=False, cancel_futures=True)


# ✅ Singleton global pour import: `from ...ia_server_whisper_service import ia_server_whisper_service`
IA_SERVER_BASE_URL = os.getenv("IA_SERVER_BASE_URL", "http://127.0.0.1:8000")
IA_SERVER_TIMEOUT = float(os.getenv("IA_SERVER_TIMEOUT", "30"))
ia_server_whisper_service: IaServerWhisperService = IaServerWhisperService(
    baseUrl=IA_SERVER_BASE_URL,
    timeout=IA_SERVER_TIMEOUT,
)
