import pyautogui
from PySide6.QtWidgets import QApplication

from modules.parlia.ui.transcription_panel import TranscriptionPanel


def copy_to_clipboard(text: str):
    """
    Copy the given text to the system clipboard.
    """
    clipboard = QApplication.clipboard()
    clipboard.setText(text)
    print(f"Text copied to clipboard: {text}")


def focus_vs_code():
    # Use OS-specific commands to bring VS Code to front
    pass


def copy_chatrelay_text():
    """
    Copy the text '[ChatRelay]' to the clipboard.
    """
    text = "[ChatRelay]"
    copy_to_clipboard(text)
    print("Text '[ChatRelay]' copied to clipboard.")


def simulate_ctrl_a():
    """
    Simulate pressing CTRL+A (select all).
    """
    pyautogui.hotkey("ctrl", "a")
    print("Simulated CTRL+A")


def simulate_ctrl_c():
    """
    Simulate pressing CTRL+C (copy).
    """
    pyautogui.hotkey("ctrl", "c")
    print("Simulated CTRL+C")


def simulate_ctrl_v():
    """
    Simulate pressing CTRL+V (paste).
    """
    pyautogui.hotkey("ctrl", "v")
    print("Simulated CTRL+V")


def simulate_enter():
    """
    Simulate pressing ENTER.
    """
    pyautogui.press("enter")
    print("Simulated ENTER")


def simulate_paste_and_confirm():
    """
    Helper function to chain CTRL+V + ENTER.
    """
    simulate_ctrl_v()
    simulate_enter()
    print("Simulated paste and confirm (CTRL+V + ENTER)")


def copy_text(transcription_panel: TranscriptionPanel):
    text = transcription_panel.get_transcription_text()
    copy_to_clipboard(text)
    print(f"Transcription text copied to clipboard: {text}")
