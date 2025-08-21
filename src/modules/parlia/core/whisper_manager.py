# === FICHIER : whisper_manager.py ===
# 🔍 Audit final du gestionnaire singleton de Whisper dans Parlia
# --------------------------------------------------
# ✅ Rôle : centralise le chargement, l’accès, la transcription, et l’état du modèle Whisper
# --------------------------------------------------

# ✅ Points positifs :
# - Singleton implicite via _current_model global : simple et efficace
# - Gestion des chemins utilisateur et modèles intégrés bien faite
# - Renvoie `parlia_state.set_whisper_ready(True/False)` = bon couplage état
# - Toutes les fonctions sont testables isolément

# 🛠 Recommandations facultatives :
# 1. 🔁 Ajouter un logger (`logger.info`) au lieu des `print()`
# 2. 🔄 Ajouter une fonction `ping_model()` pour tester si le modèle répond vite (ex : transcription vide ou courte)
# 3. 🔁 Passer `get_model()` en property si accédé souvent (`model = whisper_manager.model`)
# 4. 🧪 Ajouter un mode `simulate=True` pour tests unitaires

# ✅ Aucun problème bloquant. Fichier parfaitement sain.

import logging
from pathlib import Path
from typing import Optional

import whisper  # Assure-toi d’avoir `openai-whisper` installé via `pip install -U openai-whisper`

from modules.parlia.services.parlia_state_manager import parlia_state

# Configuration du logger
from src.core.logger_manager import get_logger

logger = get_logger("whisper")

logger.setLevel(logging.DEBUG)

_current_model: Optional[whisper.Whisper] = None


def load_model(model_path: str) -> None:
    """
    Charge un modèle Whisper, soit depuis un nom intégré, soit depuis un fichier dans le dossier utilisateur.
    """
    global _current_model

    if _current_model is not None:
        logger.info("Un modèle est déjà chargé. Déchargement en cours...")
        unload_model()

    # Cas 1 : modèle intégré (fourni par Whisper directement)
    if model_path in ["tiny", "base", "small", "medium", "large"]:
        logger.info(f"Chargement du modèle Whisper intégré : {model_path}")
        _current_model = whisper.load_model(model_path)

    else:
        # Cas 2 : modèle custom => récupérer le dossier sélectionné par l'utilisateur
        from modules.parlia.services.parlia_data import get_model_folder_path

        model_dir = get_model_folder_path()

        if not model_dir:
            logger.error("Aucun dossier modèle défini dans les préférences utilisateur.")
            return

        full_path = Path(model_dir) / model_path

        if full_path.exists():
            logger.info(f"Chargement du modèle Whisper depuis fichier : {full_path.resolve()}")
            _current_model = whisper.load_model(str(full_path))
        else:
            logger.error(f"Le modèle spécifié est introuvable : {full_path}")
            return

    logger.info(f"✅ Modèle chargé avec succès : {model_path}")
    parlia_state.set_whisper_ready(True)


def unload_model() -> None:
    """
    Décharge le modèle actuellement chargé.
    """
    global _current_model

    if _current_model is None:
        logger.info("Aucun modèle à décharger.")
        return

    logger.info("Déchargement du modèle.")
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

    logger.info("Lancement de la transcription réelle via Whisper.")
    result = _current_model.transcribe(audio_path)

    # Ajout d’un log pour vérification
    logger.debug(f"Résultat brut de Whisper : {result}")

    text = result.get("text", "")
    if isinstance(text, str):
        return text.strip()
    else:
        return ""
