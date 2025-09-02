# src/modules/parlia/services/audioService.py
from __future__ import annotations

import json
import os
import time
import wave
from pathlib import Path
from typing import Any, Callable, Optional, Protocol, TypeAlias

# --- imports (ajouter QTimer) ---
from PySide6.QtCore import QObject, QThread, QTimer, QUrl, Signal, Slot  # ⬅️ NEW
from PySide6.QtNetwork import QAbstractSocket
from PySide6.QtWebSockets import QWebSocket

from src.core.logger_manager import get_logger
from src.modules.parlia.services.ia_server_service import ia_server_service
from src.modules.parlia.services.parlia_data import get_max_duration


# -- Protocols --
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
            try:
                data = stream.read(1024)
            except Exception as e:
                logger.error(f"Erreur lecture flux audio: {e}")
                break
            else:
                self.frames.append(data)
                elapsed = time.monotonic() - self.service.start_time
                self.update_time.emit(elapsed)

        if (time.monotonic() - self.service.start_time) >= self.service.max_duration:
            logger.info("⏱️ Limite atteinte, arrêt automatique de l’enregistrement.")
            self.service.recordingStoppedByLimit.emit()

        try:
            if stream:
                stream.stop_stream()
                stream.close()
        except Exception as e:
            logger.error(f"Erreur fermeture flux audio: {e}")
        finally:
            self.service.stream = None

        saved_path = self.service._save_audio(self.frames)
        path_str = str(saved_path) if saved_path else ""
        logger.info("💾 Enregistrement terminé.")
        self.service.recordingFinished.emit(path_str)
        self.finished.emit()


# --- Streaming worker (envoi progressif des frames) ---
# --- Streaming worker (envoi progressif des frames) ---
class StreamingRecorder(QObject):
    finished = Signal()
    update_time = Signal(float)
    chunkReady = Signal(bytes)  # émis vers AudioService pour envoi WS

    def __init__(self, service: "AudioService") -> None:
        super().__init__()
        self.service = service
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
        logger.info("🎙️ Streaming audio démarré...")

        limit_emitted: bool = False  # ⬅️ NEW: évite les doublons d'event

        try:
            while self._running:
                try:
                    data = stream.read(1024)
                except Exception as e:
                    logger.error(f"Erreur lecture flux audio (streaming): {e}")
                    break
                else:
                    self.chunkReady.emit(data)
                    elapsed = time.monotonic() - self.service.start_time
                    self.update_time.emit(elapsed)

                    # ⬅️ NEW: signaler la limite atteinte sans arrêter le flux
                    if (not limit_emitted) and (elapsed >= self.service.max_duration):
                        logger.warning("⚠️ Limite dépassée (streaming), le flux continue.")
                        try:
                            self.service.recordingLimitReached.emit()
                        except Exception:
                            pass
                        limit_emitted = True
        finally:
            try:
                stream.stop_stream()
                stream.close()
            except Exception:
                pass
            self.service.stream = None
            self.finished.emit()


class AudioService(QObject):
    recordingFinished = Signal(str)
    recordingStoppedByLimit = Signal()
    recordingLimitReached = Signal()
    partialTranscriptAvailable = Signal(str)

    def __init__(self, max_duration: int = 60) -> None:
        super().__init__()
        self.max_duration: int = max_duration
        self.output_path: Optional[Path] = None
        self.is_recording: bool = False
        self.is_streaming: bool = False
        self.start_time: Optional[float] = None

        self.audio: Optional[AudioType] = pyaudio.PyAudio() if pyaudio else None
        self.stream: Optional[StreamType] = None

        self._thread: Optional[QThread] = None
        self._worker: Optional[AudioRecorder] = None

        # streaming
        self._streamThread: Optional[QThread] = None
        self._streamWorker: Optional[StreamingRecorder] = None
        self._socket: Optional[QWebSocket] = None

        # ⬅️ NEW: fermeture gracieuse (attente du transcript final)
        self._awaitingFinal: bool = False
        self._gracefulTimer: QTimer = QTimer(self)
        self._gracefulTimer.setSingleShot(True)
        self._gracefulTimer.timeout.connect(self._onGracefulTimeout)
        self._finalTimeoutMs: int = 4000

        Path("recordings").mkdir(parents=True, exist_ok=True)

    # --- Non-streaming (existant) ---

    def _build_output_path(self) -> Path:
        base_dir = Path("recordings")
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir / "recording.wav"

    def start_recording(self) -> None:
        if self.is_recording:
            raise RuntimeError("Enregistrement déjà en cours.")
        if not self.audio:
            raise RuntimeError("PyAudio non disponible.")

        self.max_duration = get_max_duration() * 60
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

        if self._worker:
            self._worker.stop()
        self.stream = None

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
        if self._streamWorker:
            self._streamWorker.update_time.connect(slot)

    def get_elapsed_time(self) -> float:
        if (not self.is_recording and not self.is_streaming) or self.start_time is None:
            return 0.0
        return time.monotonic() - self.start_time

    def get_last_audio_path(self) -> str:
        return str(self.output_path) if self.output_path else ""

    def _save_audio(self, frames: list[bytes]) -> Optional[Path]:
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

        Path(self.output_path.parent).mkdir(parents=True, exist_ok=True)
        tmp_path = self.output_path.with_suffix(".tmp")
        try:
            with wave.open(str(tmp_path), "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b"".join(frames))
            os.replace(tmp_path, self.output_path)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde audio: {e}")
            try:
                if tmp_path.exists():
                    tmp_path.unlink(missing_ok=True)
            except Exception:
                pass
            return None

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

    # --- Streaming (nouveau) ---

    def startStreamingRecording(self) -> None:
        if self.is_streaming:
            raise RuntimeError("Streaming déjà en cours.")
        if not self.audio:
            raise RuntimeError("PyAudio non disponible.")

        self.max_duration = get_max_duration() * 60
        self.is_streaming = True

        # ⬅️ NEW: reset fermeture gracieuse
        self._awaitingFinal = False
        if self._gracefulTimer.isActive():
            self._gracefulTimer.stop()

        # socket WS (texte: partiels; binaire: audio PCM16 mono 44.1kHz)
        self._socket = QWebSocket()
        self._socket.connected.connect(self._onSocketConnected)
        self._socket.disconnected.connect(self._onSocketDisconnected)
        self._socket.textMessageReceived.connect(self._onSocketText)
        self._socket.errorOccurred.connect(self._onSocketError)

        ws_url = self._computeWsUrl()
        logger.info(f"🚀 Ouverture WebSocket vers: {ws_url}")
        self._socket.open(QUrl(ws_url))

    def stopStreamingRecording(self) -> None:
        # ⬅️ NEW: délégué vers la fermeture gracieuse
        self.stopStreaming()

    def stopStreaming(self) -> None:
        """
        Ferme proprement le streaming avec délai de flush:
        - stop capture micro immédiatement
        - attend ~1s avant d'envoyer {"type":"end"} pour laisser passer les derniers chunks
        - attend le transcript final (via _onSocketText) avec timeout
        - ferme le WebSocket proprement
        """
        if not self.is_streaming and self._socket is None:
            logger.info("stopStreaming() ignoré : pas de streaming actif.")
            return

        # 1) arrêter la capture micro immédiatement (plus aucun chunk émis)
        try:
            if self._streamWorker:
                self._streamWorker.stop()
            if self._streamThread:
                self._streamThread.quit()
                self._streamThread.wait()
        except Exception as e:
            logger.error(f"Erreur arrêt thread streaming: {e}")
        finally:
            self._streamThread = None
            self._streamWorker = None

        self.is_streaming = False  # acquisition stoppée, socket toujours ouverte

        # 2) laisser le WS actif et différer l'envoi du "end" pour flush
        logger.info("🛑 Stop demandé, attente 1s pour flush audio...")

        def _send_end_after_flush() -> None:
            try:
                if (
                    self._socket
                    and self._socket.state() == QAbstractSocket.SocketState.ConnectedState
                ):
                    logger.info("📤 Envoi 'end' après flush.")
                    self._socket.sendTextMessage(json.dumps({"type": "end"}))
                    # 3) démarrer l'attente du transcript final
                    self._awaitingFinal = True
                    self._gracefulTimer.start(self._finalTimeoutMs)
                else:
                    logger.warning("WebSocket non connecté après flush, fermeture immédiate.")
                    self._closeWebSocket("socket not connected after flush")
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi du message 'end' après flush: {e}")
                self._closeWebSocket("error while sending end after flush")

        # ⬅️ délai non bloquant (UI safe)
        QTimer.singleShot(1000, _send_end_after_flush)

    # --- WS plumbing ---

    @Slot()
    def _onSocketConnected(self) -> None:
        logger.info("✅ WS streaming connecté.")

        # reset du timer si besoin
        if self._gracefulTimer.isActive():
            self._gracefulTimer.stop()
        self._awaitingFinal = False

        # handshake START obligatoire
        try:
            if self._socket is not None:
                self._socket.sendTextMessage(
                    json.dumps(
                        {
                            "type": "start",
                            "language": "fr",
                            "beam_size": 5,
                            "vad": True,
                            "sample_rate": 44100,
                        }
                    )
                )
                logger.info("📤 Handshake 'start' envoyé au serveur.")
        except Exception as e:
            logger.error(f"Erreur envoi handshake start: {e}")

        # démarrer le thread d’acquisition uniquement après connexion WS
        self._streamThread = QThread()
        self._streamWorker = StreamingRecorder(self)
        self._streamWorker.moveToThread(self._streamThread)
        self._streamThread.started.connect(self._streamWorker.run)
        self._streamWorker.finished.connect(self._streamThread.quit)
        self._streamWorker.finished.connect(self._streamWorker.deleteLater)
        self._streamThread.finished.connect(self._streamThread.deleteLater)

        # envoi des chunks depuis worker → socket (thread UI)
        self._streamWorker.chunkReady.connect(self._onChunkReady)

        self._streamThread.start()

    @Slot()
    def _onSocketDisconnected(self) -> None:
        logger.warning("WS streaming déconnecté.")

    @Slot(str)
    def _onSocketText(self, message: str) -> None:
        # parse JSON serveur: { "partial": "..." } / { "text": "...", "final": true }
        try:
            data = json.loads(message)
            if isinstance(data, dict):
                text = str(data.get("partial", "") or data.get("text", "")) if data else ""
                if text:
                    self.partialTranscriptAvailable.emit(text)
                is_final = bool(data.get("final", False))
                if is_final:
                    logger.info("🧾 Transcript final reçu (streaming).")
                    # ⬅️ on peut fermer proprement maintenant
                    self._awaitingFinal = False
                    self._closeWebSocket("final transcript received")
        except Exception as e:
            logger.error(f"WS streaming message invalide: {e}")

    def _closeWebSocket(self, reason: str) -> None:
        """Ferme le WebSocket si encore ouvert (nettoyage et logs)."""
        try:
            if self._gracefulTimer.isActive():
                self._gracefulTimer.stop()
        except Exception:
            pass

        if self._socket:
            try:
                state = self._socket.state()
                if state != QAbstractSocket.SocketState.UnconnectedState:
                    logger.info(f"🔌 Fermeture WebSocket ({reason}).")
                    self._socket.close()
                else:
                    logger.info(f"WebSocket déjà fermé ({reason}).")
            except Exception as e:
                logger.error(f"Erreur lors de la fermeture WS: {e}")
            finally:
                pass
        else:
            logger.info(f"Aucun WebSocket actif ({reason}).")

    @Slot()
    def _onGracefulTimeout(self) -> None:
        """Timeout d'attente du transcript final → fermeture forcée."""
        if not self._awaitingFinal:
            return
        logger.warning("⏳ Aucun transcript final reçu, fermeture WS par timeout.")
        self._awaitingFinal = False
        self._closeWebSocket("final timeout")

    @Slot(QAbstractSocket.SocketError)
    def _onSocketError(self, err: QAbstractSocket.SocketError) -> None:
        # Qt donne aussi une description textuelle via errorString()
        if self._socket:
            msg = self._socket.errorString()
        else:
            msg = "Socket non initialisée"

        logger.error(f"WS streaming erreur ({err}): {msg}")

    @Slot(bytes)
    def _onChunkReady(self, chunk: bytes) -> None:
        """Convertit un chunk audio en base64 et l’envoie au serveur WS."""
        import base64

        try:
            if self._socket:
                b64_chunk = base64.b64encode(chunk).decode("ascii")
                msg = {"type": "audio_chunk", "data": b64_chunk}
                self._socket.sendTextMessage(json.dumps(msg))
        except Exception as e:
            logger.error(f"Erreur envoi chunk WS: {e}")

    def _computeWsUrl(self) -> str:
        base = getattr(ia_server_service, "baseUrl", "http://127.0.0.1:8000")
        # endpoint réel: /whisper/ws/transcribe
        if base.startswith("https://"):
            return f"wss://{base[len('https://') :]}/whisper/ws/transcribe"
        if base.startswith("http://"):
            return f"ws://{base[len('http://') :]}/whisper/ws/transcribe"
        return f"ws://{base}/whisper/ws/transcribe"

    def __del__(self) -> None:
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
            try:
                if self.audio:
                    self.audio.terminate()
            except Exception:
                pass


# ✅ Singleton
audio_service: AudioService = AudioService()
