from __future__ import annotations

import os
import time
import wave
from pathlib import Path
from typing import Any, Callable, Optional, Protocol, TypeAlias

from PySide6.QtCore import QObject, QThread, Signal

from src.core.logger_manager import get_logger


# -- Fix Pyright: on définit des Protocols plutôt que référencer directement pyaudio.*
class StreamLike(Protocol):
    def read(self, num_frames: int) -> bytes: ...
    def stop_stream(self) -> None: ...
    def close(self) -> None: ...


class AudioLike(Protocol):
    # Typage explicite des varargs pour MyPy
    def open(self, *args: Any, **kwargs: Any) -> StreamLike: ...
    def get_format_from_width(self, width: int) -> int: ...
    def get_sample_size(self, fmt: int) -> int: ...
    def terminate(self) -> None: ...


AudioType: TypeAlias = AudioLike
StreamType: TypeAlias = StreamLike

try:
    import pyaudio as _pyaudio
except ImportError:
    _pyaudio = None

# -- Typage explicite pour aider Pyright dans les gardes runtime
pyaudio: Optional[Any] = _pyaudio

logger = get_logger("AudioService")


class AudioRecorder(QObject):
    finished = Signal()
    update_time = Signal(float)

    def __init__(self, service: AudioService) -> None:
        super().__init__()
        self.service: AudioService = service
        self.frames: list[bytes] = []
        self._running: bool = True

    def stop(self) -> None:
        self._running = False

    def run(self) -> None:
        if not self.service.audio:
            raise RuntimeError("PyAudio non disponible.")

        stream = self.service.audio.open(
            format=self.service.audio.get_format_from_width(2),
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024,
        )
        self.service.stream = stream
        self.service.start_time = time.monotonic()
        logger.info("🎙️ Enregistrement démarré...")

        while (
            self._running
            and (time.monotonic() - self.service.start_time) < self.service.max_duration
        ):
            data = stream.read(1024)
            self.frames.append(data)
            elapsed = time.monotonic() - self.service.start_time
            self.update_time.emit(elapsed)

        self.service._save_audio(self.frames)
        logger.info("💾 Enregistrement terminé.")
        self.finished.emit()


class AudioService:
    def __init__(self, max_duration: int = 60) -> None:
        self.max_duration: int = max_duration
        self.output_path: Path = Path("temp_audio") / "current_record.wav"
        self.is_recording: bool = False
        self.start_time: Optional[float] = None

        self.audio: Optional[AudioType] = pyaudio.PyAudio() if pyaudio else None
        self.stream: Optional[StreamType] = None
        self._thread: Optional[QThread] = None
        self._worker: Optional[AudioRecorder] = None

        os.makedirs(self.output_path.parent, exist_ok=True)

    def start_recording(self) -> None:
        if self.is_recording:
            raise RuntimeError("Enregistrement déjà en cours.")

        self.is_recording = True
        self._thread = QThread()
        self._worker = AudioRecorder(self)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

    def stop_recording(self) -> str:
        if not self.is_recording:
            raise RuntimeError("Aucun enregistrement en cours.")
        self.is_recording = False

        if self._worker:
            self._worker.stop()

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        return str(self.output_path)

    def connect_timer(self, slot: Callable[[float], None]) -> None:
        if self._worker:
            self._worker.update_time.connect(slot)

    def get_elapsed_time(self) -> float:
        if not self.is_recording or self.start_time is None:
            return 0.0
        return time.monotonic() - self.start_time

    def get_last_audio_path(self) -> str:
        return str(self.output_path)

    def _save_audio(self, frames: list[bytes]) -> None:
        if not pyaudio:
            raise RuntimeError("PyAudio n'est pas disponible.")
        if not self.audio:
            raise RuntimeError("L'objet PyAudio n'a pas pu être initialisé.")

        with wave.open(str(self.output_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b"".join(frames))

    def __del__(self) -> None:
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()


# ✅ Singleton global
audio_service: AudioService = AudioService()
