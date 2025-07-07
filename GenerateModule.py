import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODULES_BASE = os.path.join(SCRIPT_DIR, "src", "modules")
SUBFOLDERS = ["services", "ui", "db", "tests", "assets"]

SRC_PATH = os.path.join(SCRIPT_DIR, "src")
sys.path.insert(0, SRC_PATH)

from models.module_info import ModuleInfo


def create_folder_with_init(path):
    os.makedirs(path, exist_ok=True)
    init_file = os.path.join(path, "__init__.py")
    open(init_file, "a").close()


def create_module(module_name, description=""):
    module_path = os.path.join(MODULES_BASE, module_name)

    if os.path.exists(module_path):
        print(f"⚠️ Le module '{module_name}' existe déjà. Abandon.")
        return

    print(f"🚀 Création du module : {module_name}")
    os.makedirs(module_path, exist_ok=True)

    # 💡 Création d'un README.md vide dans le module
    readme_path = os.path.join(module_path, "README.md")
    with open(readme_path, "w", encoding="utf-8") as readme_file:
        readme_file.write("")

    for sub in SUBFOLDERS:
        sub_path = os.path.join(module_path, sub)
        create_folder_with_init(sub_path)

    # Création de l'objet ModuleInfo avec les infos de base
    module_info = ModuleInfo(
        name=module_name,
        description=description,
        icon_path=f"assets/{module_name}.png",
    )

    # Écriture du __init__.py complet
    init_file_path = os.path.join(module_path, "__init__.py")
    with open(init_file_path, "w", encoding="utf-8") as f:
        f.write(f"# __init__.py – Métadonnées du module {module_name}\n\n")
        relative_import = "from models.module_info import ModuleInfo as BaseModuleInfo"
        f.write(relative_import + "\n\n")

        # Variables individuelles (lisibles et modifiables à la main)
        for key, value in module_info.__dict__.items():
            f.write(f"{key} = {repr(value)}\n")

        f.write(
            "\n\n"
            "def launch(parent=None):\n"
            "    # Fonction à implémenter : retourne un QWidget pour lancer le module\n"
            "    return None\n\n"
        )

        # Instanciation de l’objet attendu
        f.write("ModuleInfo = BaseModuleInfo(\n")
        for key in module_info.__dict__.keys():
            f.write(f"    {key}={key},\n")
        f.write(")\n")

    print(f"✅ Module '{module_name}' créé avec toutes les métadonnées par défaut.")


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
