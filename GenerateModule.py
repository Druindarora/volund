import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_BASE = os.path.join(SCRIPT_DIR, "src", "modules")
SUBFOLDERS = ["core", "services", "ui", "db", "tests", "assets"]
SRC_PATH = os.path.join(SCRIPT_DIR, "src")
sys.path.insert(0, SRC_PATH)

from models.module_info import ModuleInfo


def create_folder_with_init(path):
    os.makedirs(path, exist_ok=True)
    init_file = os.path.join(path, "__init__.py")
    open(init_file, "a").close()


def stylesheet_contains():
    return """\
# modules/xxxx/utils/stylesheet_loader.py

import inspect
import os
from typing import Optional

def load_qss_for(widget, stylesheet_name: Optional[str] = None):

    # Charge un fichier QSS situé dans ../assets/styles/
    # Si `stylesheet_name` est None :
    #     → on déduit automatiquement à partir du fichier panel (ex: transcription_panel.py → transcription_style.qss)
    # Sinon :
    #     → on cherche le fichier {stylesheet_name}.qss

    # Fichier appelant
    caller_file = inspect.stack()[1].filename
    base_dir = os.path.dirname(caller_file)

    # Nom du fichier à charger
    if stylesheet_name is None:
        panel_file = os.path.basename(caller_file)
        panel_prefix = panel_file.split("_panel.py")[0]
        qss_file = f"{panel_prefix}_style.qss"
    else:
        qss_file = f"{stylesheet_name}.qss"

    qss_path = os.path.abspath(
        os.path.join(base_dir, "..", "assets", "styles", qss_file)
    )

    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            widget.setStyleSheet(f.read())
        print(f"[STYLE] QSS chargé : {qss_path}")
    else:
        print(f"[STYLE] Aucun QSS trouvé : {qss_path} (non bloquant)")

        """


def create_module(module_name: str, description: str = ""):
    module_name_lower = module_name.lower()
    module_path = os.path.join(MODULES_BASE, module_name_lower)

    if os.path.exists(module_path):
        print(f"⚠️ Le module '{module_name}' existe déjà. Abandon.")
        return

    print(f"🚀 Création du module : {module_name}")
    os.makedirs(module_path, exist_ok=True)

    # README
    readme_path = os.path.join(module_path, "README.md")
    with open(readme_path, "w", encoding="utf-8") as readme_file:
        readme_file.write(
            "# 📘 À remplir dès que possible : description du module, objectifs, contexte...\n"
        )

    # Dossiers avec __init__.py
    for sub in SUBFOLDERS:
        sub_path = os.path.join(module_path, sub)
        create_folder_with_init(sub_path)

    # Dossier assets/styles (⚠️ vide, mais toujours présent)
    styles_path = os.path.join(module_path, "assets", "styles")
    os.makedirs(styles_path, exist_ok=True)

    # Fichier settings.py
    settings_path = os.path.join(module_path, "settings.py")
    with open(settings_path, "w", encoding="utf-8") as settings_file:
        settings_file.write(f"# 🛠️ Paramètres du module {module_name}\n\n")
        settings_file.write("LABELS = {\n")
        settings_file.write('    "home_title": "Bienvenue dans ce nouveau module",\n')
        settings_file.write("}\n")

    # Fichier utils/stylesheet_loader.py
    utils_path = os.path.join(module_path, "utils")
    os.makedirs(utils_path, exist_ok=True)
    with open(
        os.path.join(utils_path, "stylesheet_loader.py"), "w", encoding="utf-8"
    ) as style_file:
        style_file.write(stylesheet_contains())

    # Fichier ui/home_panel.py
    home_panel_path = os.path.join(module_path, "ui", "home_panel.py")
    with open(home_panel_path, "w", encoding="utf-8") as home_file:
        home_file.write(f"""\
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from ..settings import LABELS

class HomePanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel(f"{{LABELS['home_title']}} : {module_name}")
        layout.addWidget(label)
        self.setLayout(layout)
""")

    # Création du __init__.py racine avec ModuleInfo
    init_file_path = os.path.join(module_path, "__init__.py")
    module_info = ModuleInfo(
        name=module_name,
        description=description,
        icon_path=f"assets/images/{module_name_lower}.png",
    )

    with open(init_file_path, "w", encoding="utf-8") as f:
        f.write(f"# __init__.py – Métadonnées du module {module_name}\n\n")
        f.write("from PySide6.QtWidgets import QWidget\n\n")
        f.write("from models.module_info import ModuleInfo as BaseModuleInfo\n\n")
        f.write(f"from modules.{module_name_lower}.ui.home_panel import HomePanel\n\n")
        for key, value in module_info.__dict__.items():
            f.write(f"{key} = {repr(value)}\n")

        f.write("\n\ndef launch(parent=None) -> QWidget:\n")
        f.write(
            "    # Fonction à implémenter : retourne un QWidget pour lancer le module\n"
        )
        f.write("    return HomePanel()\n\n")

        f.write("ModuleInfo = BaseModuleInfo(\n")
        for key in module_info.__dict__.keys():
            f.write(f"    {key}={key},\n")
        f.write(")\n")

    print(f"✅ Module '{module_name}' créé avec toutes les structures nécessaires.")


def main():
    if not os.path.exists(MODULES_BASE):
        print(f"❌ Dossier introuvable : {MODULES_BASE}")
        return

    if len(sys.argv) > 1:
        module_name = sys.argv[1]
    else:
        module_name = input("🔤 Entrez le nom du module à créer : ").strip()

    if not module_name:
        print("❌ Aucun nom fourni. Abandon.")
        return

    description = input("📝 Description du module (optionnel) : ").strip()
    create_module(module_name, description)


if __name__ == "__main__":
    main()
