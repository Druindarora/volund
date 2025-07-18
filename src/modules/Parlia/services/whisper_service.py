import os
from typing import Callable, Optional

from PySide6.QtCore import QObject, QThread, Signal

from modules.parlia.core.whisper_manager import is_model_loaded, transcribe
from modules.parlia.services.audioService import audio_service
from modules.parlia.services.parlia_data import (
    get_conclusion_text,
    get_include_conclusion,
)


class _AsyncTranscriber(QObject):
    finished = Signal(object)

    def __init__(self, path: str):
        super().__init__()
        self.audio_path = path

    def run(self):
        from modules.parlia.core.whisper_manager import transcribe
        from modules.parlia.services.parlia_data import (
            get_conclusion_text,
            get_include_conclusion,
        )

        try:
            text = transcribe(self.audio_path)
            if get_include_conclusion():
                conclusion = get_conclusion_text()
                if conclusion:
                    text += f"\n\n{conclusion}"
            self.finished.emit(text)
        except Exception as e:
            print(f"[ERREUR ASYNC] Transcription échouée : {e}")
            self.finished.emit(None)


class WhisperService:
    def transcribe(self, callback: Callable[[Optional[str]], None]):
        """
        Transcrit un fichier audio via WhisperManager et transmet le texte au callback.
        :param audio_path: Chemin vers le fichier .wav à transcrire.
        :param callback: Fonction à appeler une fois la transcription terminée.
        """
        audio_path = audio_service.get_last_audio_path()

        # Vérifier si un modèle est chargé
        if not is_model_loaded():
            print("[ERREUR] Aucun modèle chargé dans WhisperManager.")
            callback(None)
            return

        # Vérifier si le fichier audio existe
        if not os.path.exists(audio_path):
            print(f"[ERREUR] Fichier audio introuvable : {audio_path}")
            callback(None)
            return

        try:
            # Lancer la transcription
            print(f"[INFO] Début de la transcription pour : {audio_path}")
            transcribed_text = transcribe(audio_path)

            # Ajouter la phrase de conclusion si activée
            if get_include_conclusion():
                conclusion_text = get_conclusion_text()
                if conclusion_text:
                    transcribed_text += f"\n\n{conclusion_text}"

            print("[INFO] Transcription terminée.")
            callback(transcribed_text)
        except Exception as e:
            print(f"[ERREUR] Échec de la transcription : {e}")
            callback(None)

    def transcribe_async(self, callback: Callable[[Optional[str]], None]):
        audio_path = audio_service.get_last_audio_path()

        if not is_model_loaded():
            print("[ERREUR] Aucun modèle chargé.")
            callback(None)
            return

        if not os.path.exists(audio_path):
            print(f"[ERREUR] Fichier audio introuvable : {audio_path}")
            callback(None)
            return

        self._thread = QThread()
        self._worker = _AsyncTranscriber(audio_path)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(callback)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()


whisper_service = WhisperService()
