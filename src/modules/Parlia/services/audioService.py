# 🎙️ AudioService - Service d’enregistrement audio pour Vølund / Parlia

import os

# import threading
import time
import wave
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal

try:
    import pyaudio
except ImportError:
    pyaudio = None


class AudioRecorder(QObject):
    finished = Signal()
    update_time = Signal(float)

    def __init__(self, service):
        super().__init__()
        self.service = service
        self.frames = []
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        import time

        audio = self.service.audio
        stream = audio.open(
            format=audio.get_format_from_width(2),
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024,
        )
        self.service.stream = stream
        self.service.start_time = time.monotonic()
        print("Enregistrement démarré...")

        while (
            self._running
            and (time.monotonic() - self.service.start_time) < self.service.max_duration
        ):
            data = stream.read(1024)
            self.frames.append(data)
            elapsed = time.monotonic() - self.service.start_time
            self.update_time.emit(elapsed)

        self.service._save_audio(self.frames)
        print("Enregistrement terminé.")
        self.finished.emit()


class AudioService:
    def __init__(self, max_duration=60):
        """
        Initialise l’état interne de l’AudioService.
        :param max_duration: Durée maximale de l’enregistrement en secondes.
        """
        self.max_duration = max_duration
        self.output_path = Path("temp_audio") / "current_record.wav"
        self.is_recording = False
        self.start_time = None
        self.audio = pyaudio.PyAudio() if pyaudio else None
        self.stream = None
        self._thread = None
        self._worker = None

        os.makedirs(self.output_path.parent, exist_ok=True)

    def start_recording(self):
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

    def stop_recording(self):
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

    def connect_timer(self, slot):
        if self._worker:
            self._worker.update_time.connect(slot)

    def get_elapsed_time(self):
        """
        Retourne la durée écoulée depuis le début de l’enregistrement.
        """
        if not self.is_recording or self.start_time is None:
            return 0
        return time.monotonic() - self.start_time

    def get_last_audio_path(self) -> str:
        """
        Retourne le chemin du dernier fichier audio enregistré.
        """
        return str(self.output_path)

    def _save_audio(self, frames):
        """
        Sauvegarde les données audio dans un fichier WAV.
        """
        if not pyaudio:
            raise RuntimeError("PyAudio n'est pas disponible.")
        if not self.audio:
            raise RuntimeError("L'objet PyAudio n'a pas pu être initialisé.")

        with wave.open(str(self.output_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(44100)
            wf.writeframes(b"".join(frames))

    def __del__(self):
        """
        Libère les ressources de l’AudioService.
        """
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio:
            self.audio.terminate()


# ✅ Singleton global
audio_service = AudioService()
