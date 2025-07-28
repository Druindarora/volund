from PySide6.QtWidgets import QApplication

from src.core.logger_manager import get_logger

logger = get_logger("copy_to_clipboard")


# 💡 À migrer dans utils/clipboard_utils.py
def copy_to_clipboard(text: str):
    """
    Copy the given text to the system clipboard.
    """
    clipboard = QApplication.clipboard()
    clipboard.setText(text)
    logger.info(f"Text copied to clipboard: {text}")
