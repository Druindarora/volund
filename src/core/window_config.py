# modules/parlia/services/windows_config.py

from core.user_data_manager import user_data

# Nom du module (sans extension)
MODULE_NAME = "volund"

# Clé dans le fichier JSON dédiée à l'état de la fenêtre
WINDOW_KEY = "window_state"

# Valeurs par défaut si aucune donnée n'existe
DEFAULT_STATE = {"x": 100, "y": 100, "width": 1000, "height": 600}


def load_window_state():
    """
    Charge l'état de la fenêtre principale (écran + maximized).
    Si aucune donnée n'existe, retourne les valeurs par défaut.
    """
    data = user_data.get(MODULE_NAME, WINDOW_KEY)
    if isinstance(data, dict):
        return {
            "maximized": data.get("maximized", True),
            "screen": data.get("screen", None),
        }
    return {"maximized": True, "screen": None}


def save_window_state(maximized: bool, screen: str | None = None):
    """
    Sauvegarde uniquement l'état maximisé et l'écran courant.
    """
    state = {"maximized": maximized, "screen": screen}
    user_data.set(MODULE_NAME, WINDOW_KEY, state)
