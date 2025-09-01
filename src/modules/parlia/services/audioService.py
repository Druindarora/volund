# src/modules/parlia/services/audioService.py
from __future__ import annotations

import os
import time
import wave
from pathlib import Path
from typing import Any, Callable, Optional, Protocol, TypeAlias

from PySide6.QtCore import QObject, QThread, Signal

from src.core.logger_manager import get_logger


# -- Protocols pour Pyright/MyPy
class StreamLike(Protocol):
    def read(self, num_frames: int) -> bytes: ...
    def stop_stream(self) -> None: ...
    def close(self) -> None: ...


class AudioLike(Protocol):
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

pyaudio: Optional[Any] = _pyaudio

logger = get_logger("AudioService")


class AudioRecorder(QObject):
    finished = Signal()
    update_time = Signal(float)

    def __init__(self, service: "AudioService") -> None:
        super().__init__()
        self.service: AudioService = service
        self.frames: list[bytes] = []
        self._running: bool = True

    def stop(self) -> None:
        self._running = False

    def run(self) -> None:
        if not self.service.audio:
            raise RuntimeError("PyAudio non disponible.")

        # ouverture du flux
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

        # boucle d'acquisition robuste
        while (
            self._running
            and (time.monotonic() - self.service.start_time) < self.service.max_duration
        ):
            try:
                data = stream.read(1024)
            except Exception as e:
                # évite un crash en cas d'arrêt brutal/overflow
                logger.error(f"Erreur lecture flux audio: {e}")
                break
            else:
                self.frames.append(data)
                elapsed = time.monotonic() - self.service.start_time
                self.update_time.emit(elapsed)

        # fermeture du flux côté worker (si encore ouvert)
        try:
            if stream:
                stream.stop_stream()
                stream.close()
        except Exception as e:
            logger.error(f"Erreur fermeture flux audio: {e}")
        finally:
            self.service.stream = None

        # sauvegarde + signal de fin
        saved_path = self.service._save_audio(self.frames)
        path_str = str(saved_path) if saved_path else ""
        logger.info("💾 Enregistrement terminé.")
        self.service.recordingFinished.emit(path_str)
        self.finished.emit()


class AudioService(QObject):
    # signal émis à la fin de l'enregistrement avec le chemin du fichier (vide si rien écrit)
    recordingFinished = Signal(str)

    def __init__(self, max_duration: int = 60) -> None:
        super().__init__()
        self.max_duration: int = max_duration
        self.output_path: Optional[Path] = None  # chemin du dernier enregistrement
        self.is_recording: bool = False
        self.start_time: Optional[float] = None

        self.audio: Optional[AudioType] = pyaudio.PyAudio() if pyaudio else None
        self.stream: Optional[StreamType] = None
        self._thread: Optional[QThread] = None
        self._worker: Optional[AudioRecorder] = None

        # crée le dossier d'output à la racine du projet
        Path("recordings").mkdir(parents=True, exist_ok=True)

    def _build_output_path(self) -> Path:
        """
        Toujours le même nom pour écraser la capture précédente.
        Écriture atomique assurée dans _save_audio via os.replace().
        """
        base_dir = Path("recordings")
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir / "recording.wav"

    def start_recording(self) -> None:
        if self.is_recording:
            raise RuntimeError("Enregistrement déjà en cours.")
        if not self.audio:
            raise RuntimeError("PyAudio non disponible.")

        self.output_path = self._build_output_path()
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

        # demande d'arrêt au worker
        if self._worker:
            self._worker.stop()

        # ⚠️ NE PAS fermer le flux ici → laissé au worker
        self.stream = None

        # attendre la fin du thread (sauvegarde incluse)
        if self._thread:
            try:
                self._thread.quit()
                self._thread.wait()
            except Exception as e:
                logger.error(f"Erreur à l'attente du thread audio: {e}")
            finally:
                self._thread = None
                self._worker = None

        return str(self.output_path) if self.output_path else ""

    def connect_timer(self, slot: Callable[[float], None]) -> None:
        if self._worker:
            self._worker.update_time.connect(slot)

    def get_elapsed_time(self) -> float:
        if not self.is_recording or self.start_time is None:
            return 0.0
        return time.monotonic() - self.start_time

    def get_last_audio_path(self) -> str:
        return str(self.output_path) if self.output_path else ""

    def _save_audio(self, frames: list[bytes]) -> Optional[Path]:
        # sécurité : frames vides → pas d'écriture
        total_bytes = sum(len(ch) for ch in frames)
        if total_bytes == 0:
            logger.error("Aucune donnée audio capturée, aucun fichier écrit.")
            return None

        if not pyaudio:
            raise RuntimeError("PyAudio n'est pas disponible.")
        if not self.audio:
            raise RuntimeError("L'objet PyAudio n'a pas pu être initialisé.")
        if not self.output_path:
            self.output_path = self._build_output_path()

        # S'assure que le dossier existe
        Path(self.output_path.parent).mkdir(parents=True, exist_ok=True)

        # Écriture atomique : .tmp puis replace()
        tmp_path = self.output_path.with_suffix(".tmp")
        try:
            with wave.open(str(tmp_path), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b"".join(frames))
            # Remplace le fichier cible de façon atomique (si existant)
            os.replace(tmp_path, self.output_path)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde audio: {e}")
            # Nettoyage du tmp si échec
            try:
                if tmp_path.exists():
                    tmp_path.unlink(missing_ok=True)
            except Exception:
                pass
            return None

        # logs utiles : durée & taille
        duration = 0.0
        if self.start_time is not None:
            duration = max(0.0, time.monotonic() - self.start_time)
        try:
            file_size = os.path.getsize(self.output_path)
        except Exception:
            file_size = 0
        logger.info(
            f"Fichier sauvegardé: {self.output_path} | "
            f"durée ~ {duration:.2f}s | taille {file_size / 1024:.1f} KiB (overwrite)"
        )
        return self.output_path

    def __del__(self) -> None:
        # fermeture flux si encore ouvert
        try:
            if self.stream is not None:
                try:
                    self.stream.stop_stream()
                except Exception:
                    pass
                try:
                    self.stream.close()
                except Exception:
                    pass
                finally:
                    self.stream = None
        finally:
            # terminaison PyAudio
            try:
                if self.audio:
                    self.audio.terminate()
            except Exception:
                pass


# ✅ Singleton global
audio_service: AudioService = AudioService()
