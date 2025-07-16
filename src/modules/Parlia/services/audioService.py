# 🎙️ AudioService - Service d’enregistrement audio pour Vølund / Parlia

import os
import time
import wave
from pathlib import Path

try:
    import pyaudio
except ImportError:
    pyaudio = None


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

        os.makedirs(self.output_path.parent, exist_ok=True)

    def start_recording(self):
        """
        Lance l’enregistrement pour une durée donnée.
        """
        if not pyaudio:
            raise RuntimeError("PyAudio n'est pas disponible.")
        if not self.audio:
            raise RuntimeError("L'objet PyAudio n'a pas pu être initialisé.")
        if self.is_recording:
            raise RuntimeError("Un enregistrement est déjà en cours.")

        self.is_recording = True
        self.start_time = time.monotonic()

        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024,
        )

        frames = []
        print("Enregistrement démarré...")

        while (
            self.is_recording
            and (time.monotonic() - self.start_time) < self.max_duration
        ):
            data = self.stream.read(1024)
            frames.append(data)

        self._save_audio(frames)
        print("Enregistrement terminé.")

    def stop_recording(self):
        """
        Force l’arrêt de l’enregistrement et retourne le chemin du fichier audio enregistré.
        """
        if not self.is_recording:
            raise RuntimeError("Aucun enregistrement en cours.")

        self.is_recording = False

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        return str(self.output_path)

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
