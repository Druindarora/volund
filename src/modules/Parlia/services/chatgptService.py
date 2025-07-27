import threading
import time

import pyautogui
import pygetwindow as gw
import pyperclip
from PySide6.QtWidgets import QFileDialog, QTextEdit

from modules.parlia.config import config
from modules.parlia.services.utils import run_countdown
from modules.trakia.services.tracker_service import log_message

# Fenêtre cible pour ChatGPT (ChatRelay)
CHATGPT_WINDOW_PREFIX = "[ChatRelay]"


def looking_for_window(window_prefix: str) -> str | None:
    """Cherche une fenêtre dont le titre contient un préfixe donné."""
    return next((title for title in gw.getAllTitles() if window_prefix in title), None)


def activate_window(title: str) -> bool:
    """Active une fenêtre donnée si elle existe."""
    try:
        gw.getWindowsWithTitle(title)[0].activate()
        return True
    except IndexError:
        return False


def send_text_to_chatgpt(text: str, status_callback=None):
    """
    Lance un compte à rebours avant d'envoyer le texte à ChatGPT,
    puis enregistre le message via le tracker Trakia.
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

    def after_countdown():
        if send_to_chatgpt():
            message = pyperclip.paste()
            try:
                log_message(message)
                print("[Parlia] ✅ Message enregistré via Trakia local")
                if status_callback:
                    status_callback("✅ Message enregistré localement", True)
            except Exception as e:
                print("[Parlia] ❌ Erreur Trakia :", e)
                if status_callback:
                    status_callback("❌ Erreur lors de l’enregistrement", False)

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
        print(f"[Parlia] {error_message}")
        if status_callback:
            status_callback(error_message, False)
        return None


def format_files_for_chatgpt(file_paths: list[str]) -> str:
    """Formate une liste de fichiers pour les inclure dans une consigne ChatGPT."""
    blocks = []
    for path in file_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            blocks.append(f"=== File: {path.split('/')[-1]} ===\n{content}")
        except Exception as e:
            blocks.append(f"=== File: {path.split('/')[-1]} ===\n[Read error: {e}]")
    return "\n\n".join(blocks)


def add_files_to_text_area(text_area: QTextEdit):
    """Ajoute les fichiers sélectionnés à la zone de texte existante."""
    current_text = text_area.toPlainText().strip()
    if not current_text:
        print(
            "⚠️ Aucune consigne initiale. Ajoutez du texte avant d’attacher des fichiers."
        )
        return

    file_dialog = QFileDialog()
    file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
    file_dialog.setNameFilter("All Files (*)")

    if file_dialog.exec():
        selected_files = file_dialog.selectedFiles()
        formatted_content = format_files_for_chatgpt(selected_files)
        text_area.append(f"\n\n{formatted_content}\n")
