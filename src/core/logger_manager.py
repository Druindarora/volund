import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

APP_NAME = "Volund"


def setup_logger(debug: bool = False):
    """Configure le logger principal de Vølund."""

    if debug:
        log_dir = Path(os.getenv("TEMP", "/tmp"))
    else:
        log_dir = Path(os.getenv("LOCALAPPDATA", ".")) / APP_NAME / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "volund.log"
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    # Crée le logger principal
    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.handlers.clear()  # éviter les doublons si setup_logger est appelé plusieurs fois

    # Handler fichier avec rotation (max 5 Mo × 5 fichiers)
    file_handler = RotatingFileHandler(
        log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(file_handler)

    if debug:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(console_handler)

    logger.info("=== Lancement de Vølund ===")
    logger.info(f"Mode : {'DEBUG' if debug else 'PROD'}")
    logger.info(f"Logs enregistrés dans {log_file}")

    return logger
