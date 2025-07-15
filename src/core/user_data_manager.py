"""
UserDataManager - Gestion centralisée des fichiers de sauvegarde utilisateur pour Vølund.
Crée automatiquement le dossier `user_data/` et les fichiers JSON de chaque module si besoin.
Expose des méthodes typées et simples pour lire, écrire, charger, sauvegarder.
"""

import json
from pathlib import Path
from typing import Optional

# Dossier où seront stockés tous les fichiers utilisateur
USER_DATA_DIR = Path("user_data")

# Modules connus de Vølund
MODULES = ["parlia", "tracker", "volund"]  # à adapter si besoin

# Version actuelle du format des données utilisateur
USER_DATA_VERSION = 1


class UserDataManager:
    def __init__(self):
        """
        Initialise le gestionnaire, crée le dossier user_data s'il n'existe pas,
        et initialise les fichiers JSON pour chaque module si absents.
        """
        USER_DATA_DIR.mkdir(exist_ok=True)

        for module_name in MODULES:
            file_path = USER_DATA_DIR / f"{module_name}.json"
            if not file_path.exists():
                self._write_file(file_path, {"version": USER_DATA_VERSION, "data": {}})

    def init(self):
        """
        Initialise le répertoire user_data et crée les fichiers pour chaque module si nécessaire.
        """
        if not USER_DATA_DIR.exists():
            USER_DATA_DIR.mkdir()

        for module_name in MODULES:
            file_path = USER_DATA_DIR / f"{module_name}.json"
            if not file_path.exists():
                self._write_file(file_path, {"version": USER_DATA_VERSION, "data": {}})

    def get(self, module_name: str, key: str) -> Optional[object]:
        """
        Récupère une valeur depuis le fichier JSON du module.
        """
        data = self.load(module_name)
        return data.get(key)

    def set(self, module_name: str, key: str, value: object):
        """
        Modifie une valeur en mémoire et sauvegarde immédiatement le fichier JSON.
        """
        file_path = USER_DATA_DIR / f"{module_name}.json"
        content = self._read_file(file_path)
        content["data"][key] = value
        self._write_file(file_path, content)

    def load(self, module_name: str) -> dict:
        """
        Charge les données du module, sans les métadonnées (version).
        """
        file_path = USER_DATA_DIR / f"{module_name}.json"
        content = self._read_file(file_path)
        return content.get("data", {})

    def save(self, module_name: str, data: dict):
        """
        Sauvegarde un dictionnaire complet dans le fichier du module.
        """
        file_path = USER_DATA_DIR / f"{module_name}.json"
        content = {"version": USER_DATA_VERSION, "data": data}
        self._write_file(file_path, content)

    def _read_file(self, path: Path) -> dict:
        """
        Lit un fichier JSON en toute sécurité. Si le fichier est vide ou corrompu,
        retourne une structure vide par défaut pour éviter les plantages.
        """
        if not path.exists() or path.stat().st_size == 0:
            return {"version": USER_DATA_VERSION, "data": {}}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"[ERREUR] Fichier JSON corrompu ou vide : {path}")
            return {"version": USER_DATA_VERSION, "data": {}}

    def _write_file(self, path: Path, content: dict):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

    def get_version(self, module_name: str) -> int:
        """
        Récupère la version du fichier utilisateur du module.
        """
        file_path = USER_DATA_DIR / f"{module_name}.json"
        content = self._read_file(file_path)
        return content.get("version", 0)


# Singleton global
user_data = UserDataManager()
