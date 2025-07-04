import os
import sys

MODULES_BASE = os.path.join("Volund", "src", "modules")
SUBFOLDERS = ["services", "ui", "db", "tests", "assets"]


def create_folder_with_init(path):
    os.makedirs(path, exist_ok=True)
    init_file = os.path.join(path, "__init__.py")
    open(init_file, "a").close()


def create_module(module_name, description="", version="0.0.0"):
    module_path = os.path.join(MODULES_BASE, module_name)

    if os.path.exists(module_path):
        print(f"⚠️ Le module '{module_name}' existe déjà. Abandon.")
        return

    print(f"🚀 Création du module : {module_name}")
    os.makedirs(module_path, exist_ok=True)

    for sub in SUBFOLDERS:
        sub_path = os.path.join(module_path, sub)
        create_folder_with_init(sub_path)

    # Génération du __init__.py principal avec métadonnées
    init_file_path = os.path.join(module_path, "__init__.py")
    with open(init_file_path, "w", encoding="utf-8") as f:
        f.write(f"""# __init__.py – Métadonnées du module {module_name}

name = "{module_name}"
version = "{version}"
description = "{description}"
icon_path = "assets/{module_name}.png"

def launch(parent=None):
    # Fonction à implémenter : retourne un QWidget pour lancer le module
    return None
""")

    print(f"✅ Module '{module_name}' créé avec métadonnées par défaut.")


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
