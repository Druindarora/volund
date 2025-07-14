import threading
import time

import pyautogui
import pygetwindow as gw
import pyperclip
import requests
from PySide6.QtWidgets import QFileDialog, QTextEdit

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
    Lance un compte à rebours avant d'envoyer le texte à ChatGPT + au tracker.
    """

    def countdown_callback(msg):
        if status_callback:
            status_callback(msg, True)

    def send_to_chatgpt():
        target_title = looking_for_window(CHATGPT_WINDOW_PREFIX)
        if target_title and activate_window(target_title):
            time.sleep(config.timeouts.window_switch)
            pyperclip.copy(text)
            pyautogui.hotkey("ctrl", "v")
            pyautogui.press("enter")
            print("[Parlia] ✅ Texte collé et envoyé à ChatRelay")
            if status_callback:
                status_callback("✅ Texte envoyé à ChatGPT", True)
            return True
        else:
            print("[Parlia] ❌ Aucune fenêtre [ChatRelay] trouvée.")
            if status_callback:
                status_callback("❌ Aucune fenêtre [ChatRelay] trouvée.", False)
            return False

    def send_to_tracker():
        tracker_title = looking_for_window(TRACKER_WINDOW_PREFIX)
        if tracker_title and activate_window(tracker_title):
            print(f"[Parlia] Tracker activé : {tracker_title}")
            message = pyperclip.paste()
            status_ok = send_to_tracker_via_api(message)

            if status_ok:
                time.sleep(config.timeouts.after_paste_delay)
                pyautogui.press("enter")
                print("[Parlia] ✅ Message transmis au tracker (avec ENTER)")
                if status_callback:
                    status_callback("✅ Message transmis au tracker", True)
            else:
                print("[Parlia] ❌ Erreur API lors de l’envoi au tracker.")
                if status_callback:
                    status_callback("❌ Échec de l’envoi au tracker via l’API", False)
        else:
            print("[Parlia] ❌ Aucune fenêtre Tracker trouvée.")
            if status_callback:
                status_callback("❌ Aucune fenêtre Tracker trouvée.", False)

    def after_countdown():
        if send_to_chatgpt():
            send_to_tracker()

    def countdown_then_send():
        run_countdown(
            config.focus_countdown,
            "⏳ Vous avez {n} seconde(s) pour vous placer dans la fenêtre cible...",
            countdown_callback,
        )
        after_countdown()

    try:
        threading.Thread(target=countdown_then_send, daemon=True).start()
        return True

    except Exception as e:
        error_message = f"❌ Erreur lors de l’envoi : {e}"
        if status_callback:
            status_callback(error_message, False)
        else:
            print(f"[Parlia] {error_message}")
        return None


def send_to_tracker_via_api(message: str) -> bool:
    try:
        response = requests.post(TRACKER_API_URL, json={"message": message})
        print("[Parlia] Tracker API → Réponse :", response.json())
        return response.json().get("status") == "ok"
    except Exception as e:
        print("[Parlia] ❌ Erreur tracker API :", e)
        return False


def format_files_for_chatgpt(file_paths: list[str]) -> str:
    """
    Format a list of file contents for ChatGPT display.

    Args:
        file_paths (list[str]): List of file paths.

    Returns:
        str: Formatted string with file names and contents.
    """
    blocks = []
    for path in file_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            block = f"=== File: {path.split('/')[-1]} ===\n{content}"
            blocks.append(block)
        except Exception as e:
            blocks.append(f"=== File: {path.split('/')[-1]} ===\n[Read error: {e}]")
    return "\n\n".join(blocks)


def add_files_to_text_area(text_area: QTextEdit):
    """
    Append selected files' contents into a QTextEdit area, if there is already some user input.

    Args:
        text_area (QTextEdit): The QTextEdit widget to append to.
    """
    current_text = text_area.toPlainText().strip()
    if not current_text:
        print("⚠️ No initial instruction found. Add one before attaching files.")
        return

    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
    file_dialog.setNameFilter("All Files (*)")

    if file_dialog.exec():
        selected_files = file_dialog.selectedFiles()
        formatted_content = format_files_for_chatgpt(selected_files)
        text_area.append(f"\n\n{formatted_content}\n")
