from PySide6.QtCore import QObject, Signal

from modules.parlia.core.whisper_manager import load_model
from src.core.logger_manager import get_logger

logger = get_logger("ModelLoaderWorker")


class ModelLoaderWorker(QObject):
    finished = Signal()
    failed = Signal(str)

    def __init__(self, model_name: str):
        super().__init__()
        self.model_name = model_name

    def run(self):
        try:
            logger.info(f"[INFO] Chargement asynchrone du modèle {self.model_name}")
            load_model(self.model_name)
            self.finished.emit()
        except Exception as e:
            logger.error(f"[ERREUR] Chargement échoué : {e}")
            self.failed.emit(str(e))
