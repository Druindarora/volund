from PySide6.QtWidgets import QFileDialog, QTextEdit

from src.core.logger_manager import get_logger

logger = get_logger("chatrelay_filetools.py")


def format_files_for_chatgpt(file_paths: list[str]) -> str:
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
    current_text = text_area.toPlainText().strip()
    if not current_text:
        logger.warning(
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
