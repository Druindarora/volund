# === FICHIER : ia_server_service.py ===
from __future__ import annotations

import os
import time
from typing import Any, Optional, cast

import requests

from src.core.logger_manager import get_logger

from .ia_server_ollama_service import IaServerOllamaService
from .ia_server_types import StatusResponse
from .ia_server_whisper_service import IaServerWhisperService


class IaServerService:
    def __init__(
        self, baseUrl: str, timeout: float = 30.0, session: Optional[requests.Session] = None
    ) -> None:
        self.baseUrl: str = baseUrl.rstrip("/")
        self.timeout: float = timeout
        self.session: requests.Session = session or requests.Session()
        self.logger = get_logger("IaServerService")

        self._statusCache: Optional[StatusResponse] = None
        self._statusTs: float = 0.0

        # provider typé, sans lambda (RUF E731)
        def statusProvider() -> StatusResponse:
            return self.getStatus()

        self.whisper = IaServerWhisperService(
            baseUrl=self.baseUrl,
            timeout=self.timeout,
            session=self.session,
            statusProvider=statusProvider,
        )
        self.ollama = IaServerOllamaService(
            baseUrl=self.baseUrl,
            timeout=self.timeout,
            session=self.session,
            statusProvider=statusProvider,
        )

    def getStatus(self, force: bool = False) -> StatusResponse:
        if not force and self._statusCache is not None:
            return self._statusCache
        try:
            r = self.session.get(f"{self.baseUrl}/status", timeout=self.timeout)
            r.raise_for_status()
            dataAny: Any = r.json()
            if not isinstance(dataAny, dict):
                # réponse JSON inattendue
                raise RuntimeError("Réponse /status inattendue (type non dict)")
            data = cast(StatusResponse, dataAny)
            self._statusCache = data
            self._statusTs = time.monotonic()
            return data
        except requests.RequestException as e:
            self.logger.error(f"[Facade] /status HTTP error: {e}")
            raise RuntimeError(str(e)) from e
        except ValueError as e:
            self.logger.error(f"[Facade] /status JSON invalide: {e}")
            raise RuntimeError(str(e)) from e

    def refreshStatus(self) -> StatusResponse:
        return self.getStatus(force=True)

    def cleanup(self) -> None:
        try:
            self.whisper.cleanup()
        except Exception:
            pass
        try:
            self.ollama.cleanup()
        except Exception:
            pass
        try:
            self.session.close()
        except Exception:
            pass


# ✅ Singleton global façade
IA_SERVER_BASE_URL = os.getenv("IA_SERVER_BASE_URL", "http://192.168.0.25:8000")
IA_SERVER_TIMEOUT = float(os.getenv("IA_SERVER_TIMEOUT", "30"))
_shared_session = requests.Session()
ia_server_service: IaServerService = IaServerService(
    baseUrl=IA_SERVER_BASE_URL,
    timeout=IA_SERVER_TIMEOUT,
    session=_shared_session,
)
