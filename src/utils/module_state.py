import json
import os


def load_module_state() -> dict:
    """
    Charge le fichier JSON `config/module_state.json`.
    Retourne un dictionnaire vide si le fichier n'existe pas ou est corrompu.
    """
    file_path = os.path.join("config", "module_state.json")
    if not os.path.exists(file_path):
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError):
        print(f"⚠️ Fichier JSON corrompu ou vide : {file_path}. Réinitialisation.")
        return {}


def save_module_state(data: dict) -> None:
    """
    Sauvegarde les données dans config/module_state.json de façon atomique,
    pour éviter les corruptions lors des lectures simultanées.
    """
    import tempfile

    os.makedirs("config", exist_ok=True)
    file_path = os.path.join("config", "module_state.json")

    # Écrire dans un fichier temporaire
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", delete=False, dir="config"
    ) as tmp_file:
        json.dump(data, tmp_file, ensure_ascii=False, indent=4)
        tmp_file.flush()
        os.fsync(tmp_file.fileno())
        temp_name = tmp_file.name

    # Remplacer le fichier d'origine de façon atomique
    os.replace(temp_name, file_path)


def set_module_favorite(module_name: str, is_favorite: bool) -> None:
    """
    Modifie ou ajoute le champ `favorite` pour le module donné.
    """
    data = load_module_state()

    if module_name not in data:
        data[module_name] = {}

    data[module_name]["favorite"] = is_favorite
    save_module_state(data)
