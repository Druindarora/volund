# === FICHIER : ia_server_types.py ===
from __future__ import annotations

from typing import TypedDict


# --- TypedDicts pour /status ---
class WhisperModels(TypedDict):
    downloaded: list[str]
    current: str


class WhisperStatus(TypedDict):
    available: bool
    state: str
    models: WhisperModels
    device: str
    compute_type: str


class OllamaStatus(TypedDict):
    available: bool
    state: str
    models: list[str]


class ServicesStatus(TypedDict):
    whisper: WhisperStatus
    ollama: OllamaStatus


class StatusResponse(TypedDict):
    overall: str
    timestamp: str
    services: ServicesStatus
