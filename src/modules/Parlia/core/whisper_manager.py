# 🔄 Module singleton pour gérer le modèle Whisper dans Parlia

# Ce fichier garantit qu’un seul modèle Whisper est chargé à la fois.
# Toutes les opérations de transcription passent par ici.

import os
from typing import Optional

import whisper  # Assure-toi d’avoir `openai-whisper` installé via `pip install -U openai-whisper`

_current_model: Optional[whisper.Whisper] = None  # type: Optional[whisper.Whisper]


def load_model(model_path: str):
    """
    Charge un modèle Whisper depuis le fichier .pt ou .bin donné.
    Si un modèle est déjà chargé, il est ignoré.
    """
    global _current_model

    if _current_model is not None:
        print(f"[INFO] Un modèle est déjà chargé. Ignorer la demande.")
        return

    if not os.path.exists(model_path):
        print(f"[ERREUR] Le modèle spécifié est introuvable : {model_path}")
        return

    print(f"[INFO] Chargement du modèle Whisper depuis : {model_path}")
    _current_model = whisper.load_model(model_path)
    print(f"[INFO] Modèle chargé avec succès.")


def unload_model():
    """
    Décharge le modèle actuellement chargé.
    """
    global _current_model

    if _current_model is None:
        print("[INFO] Aucun modèle à décharger.")
        return

    print(f"[INFO] Déchargement du modèle.")
    _current_model = None


def is_model_loaded() -> bool:
    """
    Retourne True si un modèle est actuellement chargé.
    """
    return _current_model is not None


def get_model():
    """
    Retourne l’instance du modèle actuel.
    """
    return _current_model


def transcribe(audio_path: str) -> str:
    """
    Transcrit un fichier audio en texte via le modèle Whisper chargé.
    """
    if _current_model is None:
        raise RuntimeError("Aucun modèle Whisper n'est chargé.")

    print(f"[INFO] Lancement de la transcription réelle via Whisper.")
    result = _current_model.transcribe(audio_path)

    # Ajout d’un log pour vérification
    print("[DEBUG] Résultat brut de Whisper :", result)

    text = result.get("text", "")
    if isinstance(text, str):
        return text.strip()
    else:
        return ""
