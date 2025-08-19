import time

from PySide6.QtCore import QObject, Signal

from modules.parlia.core.whisper_manager import transcribe
from modules.parlia.services.parlia_data import (
    get_conclusion_text,
    get_include_conclusion,
)
from src.core.logger_manager import get_logger

logger = get_logger("TranscriberWorker")


class TranscriberWorker(QObject):
    finished = Signal(object)
    update_time = Signal(float)

    def __init__(self, path: str):
        super().__init__()
        self.audio_path = path
        self._running = True

    def run(self):
        start = time.monotonic()
        logger.info("[INFO] Lancement de la transcription réelle via Whisper.")

        try:
            # Lancer dans un thread de mesure
            def ticker():
                while self._running:
                    elapsed = time.monotonic() - start
                    self.update_time.emit(elapsed)
                    time.sleep(0.2)

            from threading import Thread

            timer_thread = Thread(target=ticker, daemon=True)
            timer_thread.start()

            # Transcription bloquante
            text = transcribe(self.audio_path)
            if get_include_conclusion():
                conclusion = get_conclusion_text()
                if conclusion:
                    text += f"\n\n{conclusion}"
            self.finished.emit(text)

        except Exception as e:
            logger.error(f"[ERREUR ASYNC] Transcription échouée : {e}")
            self.finished.emit(None)
        finally:
            self._running = False
