# === FICHIER : chatgpt_service.py ===
# ⚙️ Linux: suppression de pygetwindow (non supporté) + fallback xdotool/wmctrl

import os
import platform
import shutil
import subprocess
import threading
import time

from modules.parlia.config import config
from modules.parlia.utils.helpers import run_countdown
from modules.trakia.services.tracker_service import log_message
from src.core.logger_manager import get_logger

CHATGPT_WINDOW_PREFIX = "[ChatRelay]"
logger = get_logger("ChatGPTService")

isLinux = platform.system() == "Linux"
isWindows = platform.system() == "Windows"
isMac = platform.system() == "Darwin"

# --- helpers système ---
# (évite les imports lourds non dispo sous Linux)

def hasCmd(cmd: str) -> bool:
    return shutil.which(cmd) is not None


# --------------------
# Gestion fenêtres
# --------------------

def _findWindowTitle_linux(prefix: str) -> str | None:
    # utilise wmctrl si dispo pour lister les fenêtres
    if not hasCmd("wmctrl"):
        return None
    try:
        out = subprocess.check_output(["wmctrl", "-lx"], text=True, stderr=subprocess.DEVNULL)
        # format: 0x01200007  0 host WM_CLASS  TITLE
        for line in out.splitlines():
            if prefix in line:
                # titre = après la 3e colonne
                parts = line.split(None, 4)
                if len(parts) >= 5:
                    return parts[4]
        return None
    except Exception:
        return None


def _activateWindow_linux(title: str) -> bool:
    # active via wmctrl ou xdotool
    if hasCmd("wmctrl"):
        try:
            subprocess.check_call(["wmctrl", "-a", title], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            pass
    if hasCmd("xdotool"):
        try:
            subprocess.check_call(["xdotool", "search", "--name", title, "windowactivate"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            pass
    return False


def _findWindowTitle(prefix: str) -> str | None:
    if isLinux:
        return _findWindowTitle_linux(prefix)
    # Windows/macOS: pygetwindow
    try:
        import pygetwindow as gw  # import paresseux
        return next((t for t in gw.getAllTitles() if prefix in t), None)
    except Exception as e:
        logger.warning(f"[Parlia] ⚠️ pygetwindow indisponible: {e}")
        return None


def _activateWindow(title: str) -> bool:
    if isLinux:
        return _activateWindow_linux(title)
    try:
        import pygetwindow as gw  # import paresseux
        gw.getWindowsWithTitle(title)[0].activate()
        return True
    except Exception:
        return False


# --------------------
# Envoi du texte
# --------------------

def _pasteAndSend_linux(text: str) -> bool:
    # 1) essai clipboard (xclip/wl-copy) + coller via Ctrl+V
    pasted = False
    if hasCmd("xclip"):
        try:
            p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
            p.communicate(input=text.encode("utf-8"))
            pasted = (p.returncode == 0)
        except Exception:
            pasted = False
    elif hasCmd("wl-copy"):
        try:
            p = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE)
            p.communicate(input=text.encode("utf-8"))
            pasted = (p.returncode == 0)
        except Exception:
            pasted = False

    if pasted and hasCmd("xdotool"):
        try:
            subprocess.check_call(["xdotool", "key", "ctrl+v", "Return"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            pass

    # 2) fallback: taper le texte (peut être lent mais universel avec xdotool)
    if hasCmd("xdotool"):
        try:
            subprocess.check_call(["xdotool", "type", "--clearmodifiers", text], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.check_call(["xdotool", "key", "Return"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False

    logger.error("[Parlia] ❌ Aucun backend d'input dispo (xdotool/xclip/wl-copy manquants).")
    return False


def _pasteAndSend_desktop(text: str) -> bool:
    # Windows/macOS via pyautogui + pyperclip
    try:
        import pyautogui  # import paresseux
        import pyperclip   # import paresseux
        pyperclip.copy(text)
        pyautogui.hotkey("ctrl", "v")
        pyautogui.press("enter")
        return True
    except Exception as e:
        logger.error(f"[Parlia] ❌ Envoi clavier/clipboard échoué: {e}")
        return False


def send_text_to_chatgpt(text: str, status_callback=None):
    def countdown_callback(msg):
        if status_callback:
            status_callback(msg, True)

    def send_to_chatgpt():
        title = _findWindowTitle(CHATGPT_WINDOW_PREFIX)
        if title and _activateWindow(title):
            time.sleep(config.timeouts.window_switch)
            ok = _pasteAndSend_linux(text) if isLinux else _pasteAndSend_desktop(text)
            if ok:
                logger.info("[Parlia] ✅ Texte collé et envoyé à ChatRelay")
                if status_callback:
                    status_callback("✅ Texte envoyé à ChatGPT", True)
                try:
                    # log via clipboard si possible, sinon le texte d'origine
                    message = text
                    try:
                        import pyperclip
                        message = pyperclip.paste() or text
                    except Exception:
                        pass
                    log_message(message)
                    logger.info("[Parlia] ✅ Message enregistré via Trakia local")
                    if status_callback:
                        status_callback("✅ Message enregistré localement", True)
                except Exception as e:
                    logger.error(f"[Parlia] ❌ Erreur Trakia : {e}")
                    if status_callback:
                        status_callback("❌ Erreur lors de l’enregistrement", False)
                return True
            else:
                if status_callback:
                    status_callback("❌ Échec de l’envoi (backend input)", False)
                return False
        else:
            logger.error("[Parlia] ❌ Aucune fenêtre [ChatRelay] trouvée.")
            if status_callback:
                status_callback("❌ Aucune fenêtre [ChatRelay] trouvée.", False)
            return False

    def after_countdown():
        send_to_chatgpt()

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
        logger.error(f"[Parlia] {error_message}")
        if status_callback:
            status_callback(error_message, False)
        return None
