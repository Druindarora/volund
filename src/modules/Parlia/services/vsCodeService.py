import threading
import time

import keyboard
import pygetwindow as gw
import pyperclip

from modules.parlia.config import config
from modules.parlia.services.utils import run_countdown

# --- Constants moved to config ---
VSCODE_WINDOW_TITLE = config.vscode_window_title
DEFAULT_COUNTDOWN_MESSAGE = config.default_countdown_message

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

active_threads = []


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
                    keyboard.send("enter")
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
        finally:
            active_threads.remove(threading.current_thread())

    thread = threading.Thread(target=countdown_and_focus)
    active_threads.append(thread)
    thread.start()

    if len(active_threads) > 10:  # Limite arbitraire
        print("Trop de threads actifs !")


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
            status_callback(
                "⚠️ Aucun nom de méthode à rajouter au message, focus annulé.", False
            )
        return

    text = f"{config.focus_and_refacto} {text.strip()}"

    focus_and_paste_in_vscode(
        text=text,
        status_callback=status_callback,
        countdown_callback=countdown_callback,
    )


def explain_code_to_vscode(
    method_name: str, status_callback=None, countdown_callback=None
):
    """
    Prépare une invite d'explication pour VS Code.

    Args:
        text (str): Contenu du fichier ou méthode à expliquer.
        method_name (str | None): Nom de la méthode à expliquer, ou None pour expliquer tout le fichier.
        status_callback (callable, optional): Fonction de rappel pour afficher les messages de statut.
    """
    try:
        if method_name:
            prompt = f"Expliquez la méthode suivante : {method_name}"
        else:
            prompt = f"Expliquez le fichier"

        pyperclip.copy(prompt)

        focus_and_paste_in_vscode(
            text=prompt,
            status_callback=status_callback,
            countdown_callback=countdown_callback,
        )

    except Exception as e:
        error_message = f"❌ Erreur lors de la préparation de l'invite : {e}"
        print(error_message)
        if status_callback:
            status_callback(error_message, False)


def analyze_code_to_vscode(status_callback=None, countdown_callback=None):
    """
    Prépare une invite d'analyse pour VS Code.

    Args:
        status_callback (callable, optional): Fonction de rappel pour afficher les messages de statut.
    """
    try:
        prompt = "Peux-tu analyser ce fichier ? Je veux un retour sur : la lisibilité et la structure du code la clarté des noms (méthodes, variables)les éventuelles mauvaises pratiques ou erreurs les opportunités de refactorisation Termine par une note globale de qualité sur 10 et des suggestions d'amélioration si besoin."

        pyperclip.copy(prompt)

        focus_and_paste_in_vscode(
            text=prompt,
            status_callback=status_callback,
            countdown_callback=countdown_callback,
        )

    except Exception as e:
        error_message = f"❌ Erreur lors de la préparation de l'invite : {e}"
        print(error_message)
        if status_callback:
            status_callback(error_message, False)
