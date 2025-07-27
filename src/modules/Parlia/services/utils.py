# === FICHIER : run_countdown.py ===
# 🔄 Ce code était précédemment dans `services/utils.py` mais ne devrait pas s'y trouver.
# ✅ Proposition : le placer dans `utils/timing.py` ou `utils/helpers.py`
# --------------------------------------------------
# Rôle : afficher un décompte avec un callback facultatif pour mise à jour UI/console
# Utilisé principalement dans l’envoi différé vers ChatRelay
# --------------------------------------------------

import time


def run_countdown(seconds, message_template, callback):
    """
    Affiche un décompte en appelant le callback à chaque seconde.
    :param seconds: durée du décompte
    :param message_template: ex: "Attention, vous avez {n} seconde(s) pour vous focus sur ChatGPT..."
    :param callback: fonction appelée à chaque seconde avec le message
    """
    for i in range(seconds, 0, -1):
        if callback:
            callback(message_template.format(n=i))
        time.sleep(1)
    if callback:
        callback("")
