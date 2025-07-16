# 🎙️ AudioService - Service d’enregistrement audio pour Vølund / Parlia
#
# Ce fichier gère l’enregistrement audio brut depuis le micro.
# Il fournit une interface simple pour démarrer, arrêter et récupérer un enregistrement.
# Il est indépendant de l’UI ou de Whisper.
#
# 🔧 Méthodes attendues :
# - __init__ : initialise l’état interne (ex : micro, durée max)
# - start_recording() : lance l’enregistrement pour une durée donnée (en secondes)
# - stop_recording() : force l’arrêt et retourne le chemin du fichier audio enregistré
# - is_recording : permet de savoir si un enregistrement est en cours
# - get_elapsed_time() : retourne la durée écoulée depuis le début de l’enregistrement
#
# 💾 L’audio peut être sauvegardé dans un dossier temporaire ou désigné (par défaut `temp/record.wav`)
#
# ⏱️ Le service gère aussi un chronomètre interne basé sur datetime ou time.monotonic()
#
# 🧪 Ce module pourra être testé sans interface graphique
#
# ✅ L’intégration se fera dans TranscriptionPanel ou via WhisperService

import os
import time
import wave

try:
    import pyaudio
except ImportError:
    pyaudio = None


class AudioService:
    def __init__(self, max_duration=60, output_path="temp/record.wav"):
        """
        Initialise l’état interne de l’AudioService.
        :param max_duration: Durée maximale de l’enregistrement en secondes.
        :param output_path: Chemin du fichier audio de sortie.
        """
        self.max_duration = max_duration
        self.output_path = output_path
        self.is_recording = False
        self.start_time = None
        self.audio = pyaudio.PyAudio() if pyaudio else None
        self.stream = None

    def start_recording(self):
        """
        Lance l’enregistrement pour une durée donnée.
        """
        if not pyaudio:
            raise RuntimeError(
                "PyAudio n'est pas disponible. Veuillez l'installer pour utiliser cette fonctionnalité."
            )

        if not self.audio:
            raise RuntimeError("L'objet PyAudio n'a pas pu être initialisé.")

        if self.is_recording:
            raise RuntimeError("Un enregistrement est déjà en cours.")

        self.is_recording = True
        self.start_time = time.monotonic()

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

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

        return self.output_path

    def get_elapsed_time(self):
        """
        Retourne la durée écoulée depuis le début de l’enregistrement.
        """
        if not self.is_recording or self.start_time is None:
            return 0

        return time.monotonic() - self.start_time

    def _save_audio(self, frames):
        """
        Sauvegarde les données audio dans un fichier WAV.
        """
        if not pyaudio:
            raise RuntimeError(
                "PyAudio n'est pas disponible. Impossible de sauvegarder l'audio."
            )

        if not self.audio:
            raise RuntimeError("L'objet PyAudio n'a pas pu être initialisé.")

        with wave.open(self.output_path, "wb") as wf:
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
