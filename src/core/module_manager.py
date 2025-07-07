# src/core/module_manager.py

import importlib.util
import traceback
from pathlib import Path
from typing import List

from models.module_info import ModuleInfo


class ModuleManager:
    """
    Classe responsable de charger dynamiquement les modules présents dans src/modules/
    Chaque module doit contenir un __init__.py avec un objet ModuleInfo défini à la racine.
    """

    def __init__(self, modules_path: str = "src/modules"):
        self.modules_path = Path(modules_path)
        self.modules: List[ModuleInfo] = []

    def load_modules(self) -> None:
        """
        Parcourt tous les dossiers du répertoire modules et tente de charger les métadonnées (ModuleInfo).
        """
        if not self.modules_path.exists():
            print(f"❌ Le dossier '{self.modules_path}' est introuvable.")
            return

        for module_dir in self.modules_path.iterdir():
            if module_dir.is_dir():
                init_file = module_dir / "__init__.py"
                if init_file.exists():
                    try:
                        module_info = self._import_module_info(init_file)
                        if module_info:
                            self.modules.append(module_info)
                    except Exception as e:
                        print(
                            f"⚠️ Erreur lors du chargement du module '{module_dir.name}': {e}"
                        )
                        traceback.print_exc()

    def _import_module_info(self, init_path: Path) -> ModuleInfo | None:
        """
        Charge dynamiquement le fichier __init__.py et récupère l'objet ModuleInfo défini à la racine.
        """
        module_name = init_path.parent.name
        spec = importlib.util.spec_from_file_location(
            f"module_{module_name}", init_path
        )

        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                if hasattr(module, "ModuleInfo"):
                    return module.ModuleInfo  # L'objet doit être défini ainsi
                else:
                    print(
                        f"⛔ Le module '{module_name}' ne contient pas de variable 'ModuleInfo'."
                    )
            except Exception as e:
                print(f"💥 Échec lors de l'importation de {module_name}: {e}")
        return None

    def get_all_modules(self) -> List[ModuleInfo]:
        """
        Retourne la liste des modules chargés (objets ModuleInfo).
        """
        return self.modules
