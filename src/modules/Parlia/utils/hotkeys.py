"""
| Action                                                                                | Pourquoi                                          |
| ------------------------------------------------------------------------------------- | ------------------------------------------------- |
| 🔁 Renommer `start_hotkey_listener` → `register_hotkey_listener()`                    | Si tu ajoutes un mapping multiple                 |
| 🔁 Centraliser le mapping dans un `hotkey_registry: dict[hotkey_str, callback]`       | Pour que d'autres actions puissent être branchées |
| ➕ Ajouter des raccourcis : `Ctrl+Shift+T` → transcrire, `Ctrl+Shift+C` → copier, etc. | Tu as la base pour en faire un système complet    |

"""

from threading import Thread

import keyboard
from PySide6.QtCore import QMetaObject, Qt


def start_hotkey_listener(get_main_window, get_transcription_panel):
    """
    Lance un thread qui écoute la combinaison CTRL + SHIFT + F12 globalement.
    Il déclenche toggle_recording() sur le transcription_panel **seulement si**
    - Parlia est lancé
    - Le modèle est prêt
    """

    def listen():
        while True:
            keyboard.wait("ctrl+shift+f12")
            print("[HOTKEY] Déclenchement clavier capté")

            main_window = get_main_window()
            panel = get_transcription_panel()

            if not main_window or not panel:
                print("[HOTKEY] Fenêtre ou panneau non dispo.")
                continue

            if not getattr(panel, "model_ready", False):
                print("[HOTKEY] Modèle non prêt → action ignorée.")
                continue

            print("[HOTKEY] Réactivation de la fenêtre principale")
            main_window.showNormal()
            main_window.raise_()
            main_window.activateWindow()

            print("[HOTKEY] toggle_recording()")
            # fmt: off
            QMetaObject.invokeMethod(panel, "toggle_recording", Qt.ConnectionType.QueuedConnection)  # type: ignore[reportArgumentType]
            # fmt: on

    thread = Thread(target=listen, daemon=True)
    thread.start()
