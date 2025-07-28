import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from colorama import Fore, init

APP_NAME = "Volund"

init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    LEVEL_COLORS = {
        logging.DEBUG: Fore.CYAN + "🐛 DEBUG",
        logging.INFO: Fore.GREEN + "✅ INFO",
        logging.WARNING: Fore.YELLOW + "⚠️ WARNING",
        logging.ERROR: Fore.RED + "❌ ERROR",
        logging.CRITICAL: Fore.MAGENTA + "🔥 CRITICAL",
    }

    def format(self, record):
        level_name = self.LEVEL_COLORS.get(record.levelno, record.levelname)
        record.levelname = level_name
        return super().format(record)


def get_logger(module_name: str) -> logging.Logger:
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    logger = logging.getLogger(module_name)
    if logger.handlers:  # éviter doublons
        return logger

    logger.setLevel(logging.DEBUG)

    # Handler console coloré
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        "%(levelname)s %(asctime)s - %(message)s", datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)

    # Handler fichier classique
    file_handler = logging.FileHandler(
        logs_dir / f"{module_name}.log", encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


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
