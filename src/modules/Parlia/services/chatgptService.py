import threading
import time

import pyautogui
import pygetwindow as gw
import pyperclip
import requests

from modules.parlia.config import config
from modules.parlia.services.utils import run_countdown

# Constants
CHATGPT_WINDOW_PREFIX = "[ChatRelay]"
TRACKER_WINDOW_PREFIX = "Tracker de messages ChatGPT"
TRACKER_API_URL = "http://localhost:3001/set-message"


def looking_for_window(window_prefix: str) -> str | None:
    windows = gw.getAllTitles()
    for title in windows:
        if window_prefix in title:
            return title
    return None


def activate_window(target_title: str) -> bool:
    try:
        win = gw.getWindowsWithTitle(target_title)[0]
        win.activate()
        return True
    except IndexError:
        return False


def send_text_to_chatgpt(text: str, status_callback=None):
    """
    Lance un compte à rebours avant d'envoyer le texte à ChatGPT.
    """
    try:

        def countdown_callback(msg):
            if status_callback:
                status_callback(msg, True)

        def after_countdown():
            pyperclip.copy(text)
            to_gpt()
            if status_callback:
                status_callback("✅ Texte envoyé à ChatGPT", True)

        def countdown_then_send():
            run_countdown(
                config.focus_countdown,
                "Attention, vous avez {n} seconde(s) pour vous focus sur ChatGPT...",
                countdown_callback,
            )
            after_countdown()

        threading.Thread(target=countdown_then_send, daemon=True).start()
        return True

    except Exception as e:
        if status_callback:
            status_callback(f"❌ Erreur ChatGPT : {e}", False)
        return None


def to_gpt():
    """
    Colle et envoie le contenu du presse-papiers dans la fenêtre [ChatRelay].
    """
    target_title = looking_for_window(CHATGPT_WINDOW_PREFIX)
    if target_title and activate_window(target_title):
        time.sleep(config.timeouts.window_switch)
        pyautogui.hotkey("ctrl", "v")
        # pyautogui.press("enter")
        print("[Parlia] Texte collé et envoyé à ChatRelay")
        to_tracker()
    else:
        print("[Parlia] Aucune fenêtre [ChatRelay] trouvée.")


def to_tracker():
    """
    Envoie le texte courant au tracker via l'API, puis simule un ENTER dans la fenêtre.
    """
    target_title = looking_for_window(TRACKER_WINDOW_PREFIX)
    if target_title and activate_window(target_title):
        print(f"[Parlia] Tracker activé : {target_title}")
        message = pyperclip.paste()
        status_ok = send_to_tracker_via_api(message)
        if status_ok:
            time.sleep(config.timeouts.after_paste_delay)
            # pyautogui.press("enter")
            print("[Parlia] Entrée simulée dans Tracker")
    else:
        print("[Parlia] Aucune fenêtre Tracker trouvée.")


def send_to_tracker_via_api(message: str) -> bool:
    try:
        response = requests.post(TRACKER_API_URL, json={"message": message})
        print("Réponse Tracker :", response.json())
        return response.json().get("status") == "ok"
    except Exception as e:
        print("Erreur tracker API :", e)
        return False


def formater_fichiers_pour_chatgpt(fichiers: list[str]) -> str:
    blocs = []
    for chemin in fichiers:
        try:
            with open(chemin, "r", encoding="utf-8") as f:
                contenu = f.read()
            bloc = f"=== Fichier : {chemin.split('/')[-1]} ===\n{contenu}"
            blocs.append(bloc)
        except Exception as e:
            blocs.append(
                f"=== Fichier : {chemin.split('/')[-1]} ===\n[Erreur de lecture : {e}]"
            )
    return "\n\n".join(blocs)
