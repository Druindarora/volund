# 🔄 Module singleton pour gérer le modèle Whisper dans Parlia

# Ce fichier garantit qu’un seul modèle Whisper est chargé à la fois.
# Toutes les opérations de transcription passent par ici.

from pathlib import Path
from typing import Optional

import whisper  # Assure-toi d’avoir `openai-whisper` installé via `pip install -U openai-whisper`

from modules.parlia.services.parlia_state_manager import parlia_state

_current_model: Optional[whisper.Whisper] = None  # type: Optional[whisper.Whisper]


def load_model(model_path: str):
    """
    Charge un modèle Whisper, soit depuis un nom intégré, soit depuis un fichier dans le dossier utilisateur.
    """
    global _current_model

    if _current_model is not None:
        print("[INFO] Un modèle est déjà chargé. Ignorer la demande.")
        return

    # Cas 1 : modèle intégré (fourni par Whisper directement)
    if model_path in ["tiny", "base", "small", "medium", "large"]:
        print(f"[INFO] Chargement du modèle Whisper intégré : {model_path}")
        _current_model = whisper.load_model(model_path)

    else:
        # Cas 2 : modèle custom => récupérer le dossier sélectionné par l'utilisateur
        from modules.parlia.services.parlia_data import get_model_folder_path

        model_dir = get_model_folder_path()

        if not model_dir:
            print(
                "[ERREUR] Aucun dossier modèle défini dans les préférences utilisateur."
            )
            return

        full_path = Path(model_dir) / model_path

        if full_path.exists():
            print(
                f"[INFO] Chargement du modèle Whisper depuis fichier : {full_path.resolve()}"
            )
            _current_model = whisper.load_model(str(full_path))
        else:
            print(f"[ERREUR] Le modèle spécifié est introuvable : {full_path}")
            return

    print(f"[INFO] ✅ Modèle chargé avec succès : {model_path}")
    parlia_state.set_whisper_ready(True)


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
    parlia_state.set_whisper_ready(False)


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
