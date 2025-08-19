"""
Neutralisation du hotkey global sous Linux (Wayland/X11) pour éviter le crash.
Conserve le comportement d’origine sur Windows/macOS.
"""

import platform
from threading import Thread

from PySide6.QtCore import QMetaObject, Qt
from src.core.logger_manager import get_logger

logger = get_logger("Hotkeys")
_is_linux = platform.system() == "Linux"


def start_hotkey_listener(get_main_window, get_transcription_panel):
    """
    Lance un thread qui écoute la combinaison CTRL + SHIFT + F12 globalement.
    Sous Linux : neutralisé (pas de hook global) pour éviter l'ImportError/root.
    """

    if _is_linux:
        # Désactive proprement sous Linux/Wayland (pas de hook global possible sans root)
        logger.warning("[Hotkeys] Global hotkey désactivé sous Linux. Utilise les boutons de l'UI.")
        return

    def listen():
        try:
            import keyboard  # import paresseux pour éviter l'import sous Linux
        except Exception as e:
            logger.error(f"[Hotkeys] Impossible d'activer le hotkey global: {e}")
            return

        while True:
            keyboard.wait("ctrl+shift+f12")
            logger.info("[HOTKEY] Déclenchement clavier capté")

            main_window = get_main_window()
            panel = get_transcription_panel()

            if not main_window or not panel:
                logger.info("[HOTKEY] Fenêtre ou panneau non dispo.")
                continue

            if not getattr(panel, "model_ready", False):
                logger.info("[HOTKEY] Modèle non prêt → action ignorée.")
                continue

            logger.info("[HOTKEY] Réactivation de la fenêtre principale")
            main_window.showNormal()
            main_window.raise_()
            main_window.activateWindow()

            logger.info("[HOTKEY] toggle_recording()")
            # fmt: off
            QMetaObject.invokeMethod(panel, "toggle_recording", Qt.ConnectionType.QueuedConnection)  # type: ignore[reportArgumentType]
            # fmt: on

    thread = Thread(target=listen, daemon=True)
    thread.start()
