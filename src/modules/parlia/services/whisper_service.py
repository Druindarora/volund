# === FICHIER : whisper_service.py ===
# 🔍 Audit et stabilisation du service de transcription avec Whisper
# --------------------------------------------------
# ✅ Le service est globalement bien structuré et modulaire.
# 🔄 Quelques fonctions peuvent être simplifiées, ou isolées pour clarté.
# 🟡 La lenteur au chargement n’est pas liée à ce fichier mais au `load_model()` (manager)
# --------------------------------------------------
# ✅ Propositions :
# - Ajouter une méthode de "ping" modèle pour test plus rapide
# --------------------------------------------------


import os
from typing import Callable, Optional

from PySide6.QtCore import QThread

from modules.parlia.core.whisper_manager import is_model_loaded, transcribe
from modules.parlia.services.audioService import audio_service
from modules.parlia.services.parlia_data import (
    get_conclusion_text,
    get_include_conclusion,
)
from modules.parlia.workers.model_loader_worker import ModelLoaderWorker
from modules.parlia.workers.transcriber_worker import TranscriberWorker
from src.core.logger_manager import get_logger

logger = get_logger("WhisperService")


class WhisperService:
    def transcribe(self, callback: Callable[[Optional[str]], None]):
        """
        Transcrit un fichier audio via WhisperManager et transmet le texte au callback.
        :param audio_path: Chemin vers le fichier .wav à transcrire.
        :param callback: Fonction à appeler une fois la transcription terminée.
        """
        audio_path = audio_service.get_last_audio_path()

        if not is_model_loaded():
            logger.error("[ERREUR] Aucun modèle chargé dans WhisperManager.")
            callback(None)
            return

        if not os.path.exists(audio_path):
            logger.error(f"[ERREUR] Fichier audio introuvable : {audio_path}")
            callback(None)
            return

        try:
            logger.info(f"[INFO] Début de la transcription pour : {audio_path}")
            transcribed_text = transcribe(audio_path)

            if get_include_conclusion():
                conclusion_text = get_conclusion_text()
                if conclusion_text:
                    transcribed_text += f"\n\n{conclusion_text}"

            logger.info("[INFO] Transcription terminée.")
            callback(transcribed_text)
        except Exception as e:
            logger.error(f"[ERREUR] Échec de la transcription : {e}")
            callback(None)

    def transcribe_async(self, callback: Callable[[Optional[str]], None]):
        audio_path = audio_service.get_last_audio_path()

        if not is_model_loaded():
            logger.error("[ERREUR] Aucun modèle chargé.")
            callback(None)
            return

        if not os.path.exists(audio_path):
            logger.error(f"[ERREUR] Fichier audio introuvable : {audio_path}")
            callback(None)
            return

        self._thread = QThread()
        self._worker = TranscriberWorker(audio_path)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(callback)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()

        def on_thread_finished():
            logger.debug("[DEBUG] Thread transcription terminé proprement.")

        self._thread.finished.connect(on_thread_finished)

    def connect_transcription_timer(self, slot):
        if hasattr(self, "_worker") and self._worker:
            self._worker.update_time.connect(slot)

    def cleanup(self):
        if hasattr(self, "_thread") and self._thread.isRunning():
            logger.info("[INFO] Attente de la fin du thread transcription...")
            self._thread.quit()
            self._thread.wait()

    def load_model_async(self, model_name: str, on_finished: Optional[Callable] = None):
        self._loader_thread = QThread()
        self._loader_worker = ModelLoaderWorker(model_name)
        self._loader_worker.moveToThread(self._loader_thread)

        self._loader_thread.started.connect(self._loader_worker.run)
        if on_finished:
            self._loader_worker.finished.connect(on_finished)

        self._loader_worker.failed.connect(lambda err: logger.error(f"[ERREUR] {err}"))

        self._loader_worker.finished.connect(self._loader_thread.quit)
        self._loader_worker.finished.connect(self._loader_worker.deleteLater)
        self._loader_thread.finished.connect(self._loader_thread.deleteLater)

        self._loader_thread.start()


whisper_service = WhisperService()
