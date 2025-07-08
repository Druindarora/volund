import json
import os

from config.env import is_dev

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "config")
STATE_FILE = os.path.join(CONFIG_DIR, "dev_state.json")


def save_last_module(module_name: str):
    """Sauvegarde le dernier module visité (utilisé uniquement en dev)."""
    if not is_dev():
        return
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_module": module_name}, f)


def load_last_module() -> str | None:
    """Retourne le dernier module visité (ou None)."""
    if not is_dev():
        return None
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("last_module")
    except Exception:
        return None
