# window_config.py

# Ce fichier gère la configuration de la fenêtre principale de l'application Vølund :
# position (x, y) et taille (width, height) de la fenêtre utilisateur.

# 📦 Le fichier de configuration est un fichier JSON stocké dans :
#    config/window_state.json

# ✅ Comportement attendu :
# - Si le fichier existe : on lit les valeurs depuis ce fichier
# - Si le fichier n'existe pas : on le crée automatiquement avec des valeurs par défaut
# - On fournit une fonction `load_window_state()` qui retourne un dictionnaire avec les clés :
#     "x", "y", "width", "height"
# - On fournit une fonction `save_window_state(x, y, width, height)` qui enregistre la nouvelle configuration

# 📂 Chemin du fichier :
# - Utiliser `os.path.join()` pour pointer vers le fichier : config/window_state.json
# - Le chemin doit être relatif à la racine du projet
# - Créer le dossier `config/` s'il n'existe pas déjà (avec `os.makedirs(..., exist_ok=True)`)

# 🧩 Valeurs par défaut :
# - x = 100
# - y = 100
# - width = 1000
# - height = 600
# Ces valeurs seront utilisées si le fichier n'existe pas ou est invalide

# 🔁 Sécurité :
# - Si le fichier JSON est vide ou corrompu, on doit revenir aux valeurs par défaut
# - Les fonctions doivent être robustes aux erreurs d'ouverture/lecture/écriture

# 🔧 Fonction 1 : load_window_state()
# - Retourne un dictionnaire avec les 4 clés ("x", "y", "width", "height")
# - Vérifie si le fichier existe
#     - Si oui : lit et parse le JSON
#     - Si non : crée le fichier avec les valeurs par défaut et retourne celles-ci

# 🔧 Fonction 2 : save_window_state(x, y, width, height)
# - Écrit dans le fichier JSON les nouvelles valeurs reçues
# - Le format du JSON doit être lisible (indentation 4 espaces)

# ❗À ne pas oublier :
# - Toujours utiliser les modules standards : os, json
# - Pas de dépendances externes

# Exemple de structure retournée :
# {
#     "x": 120,
#     "y": 80,
#     "width": 1280,
#     "height": 720
# }

# 👉 Copilot doit générer deux fonctions robustes et simples :
# - load_window_state()
# - save_window_state(x, y, width, height)

import json
import os


def load_window_state():
    # Chemin du fichier de configuration
    config_dir = os.path.join(os.getcwd(), "config")
    config_file = os.path.join(config_dir, "window_state.json")

    # Valeurs par défaut
    default_state = {"x": 100, "y": 100, "width": 1000, "height": 600}

    # Vérifier si le fichier existe
    if not os.path.exists(config_file):
        # Créer le dossier si nécessaire
        os.makedirs(config_dir, exist_ok=True)
        # Écrire les valeurs par défaut dans le fichier
        with open(config_file, "w") as f:
            json.dump(default_state, f, indent=4)
        return default_state

    # Lire le fichier JSON
    try:
        with open(config_file, "r") as f:
            data = json.load(f)
            # Vérifier que toutes les clés nécessaires sont présentes
            if all(key in data for key in ["x", "y", "width", "height"]):
                return data
    except (json.JSONDecodeError, IOError):
        pass

    # En cas d'erreur ou de fichier corrompu, retourner les valeurs par défaut
    return default_state


def save_window_state(x, y, width, height):
    # Chemin du fichier de configuration
    config_dir = os.path.join(os.getcwd(), "config")
    config_file = os.path.join(config_dir, "window_state.json")

    # Créer le dossier si nécessaire
    os.makedirs(config_dir, exist_ok=True)

    # Écrire les nouvelles valeurs dans le fichier JSON
    state = {"x": x, "y": y, "width": width, "height": height}
    with open(config_file, "w") as f:
        json.dump(state, f, indent=4)
