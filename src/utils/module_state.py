# modules/core/state/module_state.py

from core.user_data_manager import user_data

MODULE_NAME = "volund"
STATE_KEY = "module_state"  # Toutes les infos seront stockées dans volund.json > data > module_state


def load_module_state() -> dict:
    """
    Charge les états des modules depuis user_data/volund.json (clé "module_state").
    Retourne un dictionnaire vide si rien n’est défini.
    """
    data = user_data.get(MODULE_NAME, STATE_KEY)
    return data if isinstance(data, dict) else {}


def save_module_state(data: dict) -> None:
    """
    Sauvegarde les états des modules dans user_data/volund.json (clé "module_state").
    """
    user_data.set(MODULE_NAME, STATE_KEY, data)


def set_module_favorite(module_name: str, is_favorite: bool) -> None:
    """
    Modifie ou ajoute le champ `favorite` pour le module donné dans le fichier user_data.
    """
    data = load_module_state()

    if module_name not in data:
        data[module_name] = {}

    data[module_name]["favorite"] = is_favorite
    save_module_state(data)
