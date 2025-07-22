# modules/parlia/utils/stylesheet_loader.py

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
