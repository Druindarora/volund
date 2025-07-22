from threading import Thread

import keyboard
import win32gui
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
