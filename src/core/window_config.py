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
    Charge la position et taille de la fenêtre principale.
    Si aucune donnée n'existe, retourne des valeurs par défaut.
    """
    data = user_data.get(MODULE_NAME, WINDOW_KEY)
    return data if isinstance(data, dict) else DEFAULT_STATE


def save_window_state(x: int, y: int, width: int, height: int):
    """
    Sauvegarde la position et la taille de la fenêtre principale dans le fichier JSON.
    """
    state = {"x": x, "y": y, "width": width, "height": height}
    user_data.set(MODULE_NAME, WINDOW_KEY, state)
