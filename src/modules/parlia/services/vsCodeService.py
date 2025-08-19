# === FICHIER : vsCodeService.py ===
# Linux: remplace pygetwindow/keyboard par wmctrl/xdotool + clipboard natif

import platform
import shutil
import subprocess
import threading
import time

from modules.parlia.config import config
from modules.parlia.services.parlia_data import get_prompt
from modules.parlia.utils.helpers import run_countdown
from src.core.logger_manager import get_logger

logger = get_logger("VSCodeService")

VSCODE_WINDOW_TITLE = config.vscode_window_title
DEFAULT_COUNTDOWN_MESSAGE = config.default_countdown_message

isLinux = platform.system() == "Linux"
isWindows = platform.system() == "Windows"
isMac = platform.system() == "Darwin"

# --- utils OS ---

def _hasCmd(cmd: str) -> bool:
    return shutil.which(cmd) is not None

# --- fenêtres ---

def get_active_window_title():
    """Retourne le titre de la fenêtre active."""
    if isLinux:
        # xdotool requis
        if not _hasCmd("xdotool"):
            return None
        try:
            return subprocess.check_output(
                ["xdotool", "getactivewindow", "getwindowname"],
                text=True, stderr=subprocess.DEVNULL
            ).strip()
        except Exception:
            return None
    else:
        try:
            import pygetwindow as gw  # import paresseux
            win = gw.getActiveWindow()
            return win.title if win else None
        except Exception:
            return None


def activate_window_by_title(window_title):
    """Donne le focus à une fenêtre par son titre."""
    if not window_title:
        return False

    if isLinux:
        # tente wmctrl puis xdotool
        if _hasCmd("wmctrl"):
            try:
                subprocess.check_call(
                    ["wmctrl", "-a", window_title],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                return True
            except Exception:
                pass
        if _hasCmd("xdotool"):
            try:
                subprocess.check_call(
                    ["xdotool", "search", "--name", window_title, "windowactivate"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                return True
            except Exception:
                pass
        return False
    else:
        try:
            import pygetwindow as gw  # import paresseux
            wins = gw.getWindowsWithTitle(window_title)
            if wins:
                wins[0].activate()
                return True
            return False
        except Exception:
            return False

# --- clipboard & input ---

def _copy_to_clipboard(text: str) -> bool:
    """Copie `text` dans le presse-papiers."""
    if isLinux:
        # xclip (X11) ou wl-copy (Wayland)
        if _hasCmd("xclip"):
            try:
                p = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
                p.communicate(input=text.encode("utf-8"))
                return p.returncode == 0
            except Exception:
                return False
        if _hasCmd("wl-copy"):
            try:
                p = subprocess.Popen(["wl-copy"], stdin=subprocess.PIPE)
                p.communicate(input=text.encode("utf-8"))
                return p.returncode == 0
            except Exception:
                return False
        # fallback: essayer pyperclip s'il est dispo/configuré
    try:
        import pyperclip  # import paresseux
        pyperclip.copy(text)
        return True
    except Exception:
        return False


def _paste_and_send_enter() -> bool:
    """Colle (Ctrl+V) puis Enter dans la fenêtre focussée."""
    if isLinux:
        if _hasCmd("xdotool"):
            try:
                subprocess.check_call(["xdotool", "key", "ctrl+v", "Return"],
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                return False
        return False
    else:
        try:
            import keyboard  # import paresseux (Windows/mac)
            keyboard.send("ctrl+v")
            time.sleep(config.timeouts.paste_delay)
            keyboard.send("enter")
            return True
        except Exception:
            # fallback pyautogui si keyboard absent
            try:
                import pyautogui
                pyautogui.hotkey("ctrl", "v")
                time.sleep(config.timeouts.paste_delay)
                pyautogui.press("enter")
                return True
            except Exception:
                return False

# --- logique principale (threadée) ---

active_threads = []

def focus_and_paste_in_vscode(text, status_callback=None, countdown_callback=None):
    """Focus VS Code et colle `text` via clipboard + envoi Enter (thread)."""

    def countdown_and_focus():
        try:
            if not _copy_to_clipboard(text):
                if status_callback:
                    status_callback("❌ Clipboard indisponible (xclip/wl-copy/pyperclip).", False)
                return

            if not activate_window_by_title(VSCODE_WINDOW_TITLE):
                if status_callback:
                    status_callback("❌ VS Code non trouvé", False)
                return

            time.sleep(config.timeouts.window_switch)

            run_countdown(config.focus_countdown, DEFAULT_COUNTDOWN_MESSAGE, countdown_callback)

            active_title = get_active_window_title()
            if active_title and VSCODE_WINDOW_TITLE in active_title:
                if _paste_and_send_enter():
                    if status_callback:
                        status_callback("✅ Texte collé et envoyé dans VS Code", True)
                else:
                    if status_callback:
                        status_callback("❌ Échec de l'envoi clavier", False)
            else:
                if status_callback:
                    status_callback("❌ Le focus n'est pas sur VS Code !", False)

        except Exception as e:
            logger.error(f"❌ Erreur : {e}")
            if status_callback:
                status_callback(f"❌ Erreur : {e}", False)
        finally:
            if threading.current_thread() in active_threads:
                active_threads.remove(threading.current_thread())

    thread = threading.Thread(target=countdown_and_focus, daemon=True)
    active_threads.append(thread)
    thread.start()

    if len(active_threads) > 10:  # limite simple
        logger.warning("Trop de threads actifs !")

# --- wrappers PySide6 ---

def focus_vscode_qt(text: str, status_callback=None, countdown_callback=None):
    if not text.strip():
        if status_callback:
            status_callback("⚠️ Aucun texte à coller, focus annulé.", False)
        return
    focus_and_paste_in_vscode(text=text, status_callback=status_callback, countdown_callback=countdown_callback)


def focus_vscode_and_refacto(text: str, status_callback=None, countdown_callback=None):
    if not text.strip():
        if status_callback:
            status_callback("⚠️ Aucun nom de méthode à rajouter au message, focus annulé.", False)
        return
    prompt_text = get_prompt("prompt_refactor")
    text = f"{prompt_text} {text.strip()}"
    focus_and_paste_in_vscode(text=text, status_callback=status_callback, countdown_callback=countdown_callback)


def explain_code_to_vscode(method_name: str, status_callback=None, countdown_callback=None):
    try:
        if method_name:
            prompt = f"Expliquez la méthode suivante : {method_name}"
        else:
            prompt = get_prompt("prompt_explain")
        _copy_to_clipboard(prompt)
        focus_and_paste_in_vscode(text=prompt, status_callback=status_callback, countdown_callback=countdown_callback)
    except Exception as e:
        msg = f"❌ Erreur lors de la préparation de l'invite : {e}"
        logger.error(msg)
        if status_callback:
            status_callback(msg, False)


def analyze_code_to_vscode(status_callback=None, countdown_callback=None):
    try:
        prompt = get_prompt("prompt_analyze")
        _copy_to_clipboard(prompt)
        focus_and_paste_in_vscode(text=prompt, status_callback=status_callback, countdown_callback=countdown_callback)
    except Exception as e:
        msg = f"❌ Erreur lors de la préparation de l'invite : {e}"
        logger.error(msg)
        if status_callback:
            status_callback(msg, False)
