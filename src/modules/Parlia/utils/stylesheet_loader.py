# === FICHIER : stylesheet_loader.py ===
# 🔍 Audit du chargeur de QSS par panel
# --------------------------------------------------
# ✅ Rôle : charger dynamiquement une feuille de style QSS pour chaque panel (via nom du fichier appelant)
# 📁 Composant utilitaire localisé dans `utils/`
# --------------------------------------------------

# ✅ Points positifs :
# - Utilisation d’`inspect.stack()` intelligente pour déterminer le nom du panel
# - Chargement depuis `assets/styles/` bien géré
# - Gestion des erreurs silencieuse mais informative

# 🛠 Suggestions (facultatives) :
# - Prévoir un `logger.info()` à la place des `print()` (console future)
# - Ajouter un paramètre `silent=True` si on veut désactiver les logs en production
# - Cacher le chemin absolu pour ne pas polluer les logs dans les builds

# ✅ Aucun refactor immédiat requis. Code clair, utile, isolé.
# Peut servir de modèle pour d’autres chargeurs (icônes, SVG, templates...)


import inspect
import os
from typing import Optional


def load_qss_for(widget, stylesheet_name: Optional[str] = None):
    """
    Charge un fichier QSS situé dans ../assets/styles/

    Si `stylesheet_name` est None :
        → on déduit automatiquement à partir du fichier panel (ex: transcription_panel.py → transcription_style.qss)

    Sinon :
        → on cherche le fichier {stylesheet_name}.qss
    """
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
