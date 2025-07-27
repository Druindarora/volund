# === FICHIER : action_service.py ===
# 🔍 Audit et réorganisation
# -----------------------------------------
# 📁 Décision : Ce fichier est un utilitaire très basique.
# Son rôle est de gérer des actions liées au presse-papiers.
# Or, ces actions sont transversales (clipboard système) :
# ✅ Proposition : déplacer ce fichier dans `utils/clipboard_utils.py`
# -----------------------------------------

from PySide6.QtWidgets import QApplication


# 💡 À migrer dans utils/clipboard_utils.py
def copy_to_clipboard(text: str):
    """
    Copy the given text to the system clipboard.
    """
    clipboard = QApplication.clipboard()
    clipboard.setText(text)
    print(f"Text copied to clipboard: {text}")


# 💡 Rôle très spécifique à ChatRelay → à intégrer dans le bouton ChatRelay du panneau concerné
# Peut être supprimé d'ici si inutilisé ailleurs
def copy_chatrelay_text():
    """
    Copy the text '[ChatRelay]' to the clipboard.
    """
    text = "[ChatRelay]"
    copy_to_clipboard(text)
    print("Text '[ChatRelay]' copied to clipboard.")


# 💡 Appartient naturellement à `transcription_panel.py`
# Cette méthode est trop dépendante de l'UI Transcription pour rester ici
def copy_text(transcription_panel):
    text = transcription_panel.get_transcription_text()
    copy_to_clipboard(text)
    print(f"Transcription text copied to clipboard: {text}")
