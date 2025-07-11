import threading
import time

import keyboard
import pygetwindow as gw
import pyperclip

from modules.parlia.config import config
from modules.parlia.services.utils import run_countdown

# Constants
VSCODE_WINDOW_TITLE = "Visual Studio Code"
DEFAULT_COUNTDOWN_MESSAGE = (
    "Attention, vous avez {n} seconde(s) pour vous focus sur VS Code..."
)

# --- Utility functions ---


def get_active_window_title():
    """
    Get the title of the currently active window.
    """
    win = gw.getActiveWindow()
    return win.title if win else None


def activate_window_by_title(window_title):
    """
    Activate a window by its title.
    """
    windows = gw.getWindowsWithTitle(window_title)
    if windows:
        windows[0].activate()
        return True
    return False


# --- Main logic (threaded) ---


def focus_and_paste_in_vscode(text, status_callback=None, countdown_callback=None):
    """
    Focus on VS Code and paste text using clipboard and keyboard emulation.
    All actions are run in a background thread.
    """

    def countdown_and_focus():
        try:
            pyperclip.copy(text)
            time.sleep(0.05)

            if activate_window_by_title(VSCODE_WINDOW_TITLE):
                time.sleep(config.timeouts.window_switch)

                countdown_seconds = config.focus_countdown
                run_countdown(
                    countdown_seconds, DEFAULT_COUNTDOWN_MESSAGE, countdown_callback
                )

                active_title = get_active_window_title()
                if active_title and VSCODE_WINDOW_TITLE in active_title:
                    keyboard.send("ctrl+v")
                    time.sleep(config.timeouts.paste_delay)
                    # keyboard.send("enter")
                    if status_callback:
                        status_callback("✅ Texte collé et envoyé dans VS Code", True)
                else:
                    if status_callback:
                        status_callback("❌ Le focus n'est pas sur VS Code !", False)
            else:
                if status_callback:
                    status_callback("❌ VS Code non trouvé", False)

        except Exception as e:
            if status_callback:
                status_callback(f"❌ Erreur : {e}", False)

    threading.Thread(target=countdown_and_focus).start()


# --- Wrapper fonctionnel pour PySide6 ---


def focus_vscode_qt(text: str, status_callback=None, countdown_callback=None):
    if not text.strip():
        if status_callback:
            status_callback("⚠️ Aucun texte à coller, focus annulé.", False)
        return

    focus_and_paste_in_vscode(
        text=text,
        status_callback=status_callback,
        countdown_callback=countdown_callback,
    )


def focus_vscode_and_refacto(text: str, status_callback=None, countdown_callback=None):
    if not text.strip():
        if status_callback:
            status_callback("⚠️ Aucun texte à coller, focus annulé.", False)
        return

    focus_and_paste_in_vscode(
        text=text,
        status_callback=status_callback,
        countdown_callback=countdown_callback,
    )
