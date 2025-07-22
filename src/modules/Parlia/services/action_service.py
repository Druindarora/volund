from PySide6.QtWidgets import QApplication

from modules.parlia.ui.transcription_panel import TranscriptionPanel


def copy_to_clipboard(text: str):
    """
    Copy the given text to the system clipboard.
    """
    clipboard = QApplication.clipboard()
    clipboard.setText(text)
    print(f"Text copied to clipboard: {text}")


def copy_chatrelay_text():
    """
    Copy the text '[ChatRelay]' to the clipboard.
    """
    text = "[ChatRelay]"
    copy_to_clipboard(text)
    print("Text '[ChatRelay]' copied to clipboard.")


def copy_text(transcription_panel: TranscriptionPanel):
    text = transcription_panel.get_transcription_text()
    copy_to_clipboard(text)
    print(f"Transcription text copied to clipboard: {text}")
