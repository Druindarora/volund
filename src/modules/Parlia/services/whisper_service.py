import os
from typing import Callable, Optional

from modules.parlia.core.whisper_manager import is_model_loaded, transcribe
from modules.parlia.services.audioService import audio_service
from modules.parlia.services.parlia_data import (
    get_conclusion_text,
    get_include_conclusion,
)

# 📦 Classe : WhisperService
#
# Ce service est responsable de la transcription audio via le modèle Whisper.
# Il est déclenché uniquement par le TranscriptionPanel une fois l’enregistrement terminé.
#
# Il utilise WhisperManager pour accéder au modèle chargé et transcrire un fichier .wav.
# Il ne connaît rien de l’interface utilisateur (aucun appel direct à l’UI).
#
# 🔹 Fonctionnement :
# - TranscriptionPanel appelle whisper_service.transcribe(audio_path, callback)
# - Le service vérifie que le modèle est chargé
# - Lance la transcription avec WhisperManager
# - Une fois la transcription terminée :
#   - il appelle callback(transcribed_text) pour transmettre le texte
# - En cas d’erreur (pas de modèle, fichier introuvable, etc.), il appelle callback(None)
#
# La méthode transcribe() est synchrone pour l’instant, mais peut évoluer vers de l’asynchrone plus tard.
#
# 🔹 À venir :
# - Ajout automatique de la phrase de conclusion (si activée)
# - Traitement des erreurs plus précis
# - Affichage de logs détaillés si nécessaire


# 🧠 Méthode : transcribe(audio_path: str, callback: Callable[[Optional[str]], None])
#
# 🔸 Paramètres :
# - audio_path : chemin vers le fichier .wav à transcrire
# - callback : fonction à appeler une fois la transcription terminée
#
# 🔸 Étapes internes :
# - Vérifie si WhisperManager a bien un modèle chargé (is_model_loaded())
# - Vérifie que le fichier existe
# - Lance la transcription via WhisperManager.transcribe(audio_path)
# - Transmet le texte résultant au callback
# - En cas d’erreur (modèle non prêt ou fichier manquant), appelle callback(None)
#
# ⚠️ L’UI (TranscriptionPanel) doit gérer la suite : affichage, erreur, etc.


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


whisper_service = WhisperService()
