import os
import sys

from PySide6.QtWidgets import QApplication

from core.logger_manager import setup_logger  # ✅ ajout du logger
from core.user_data_manager import user_data
from gui.main_window import MainWindow

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
sys.path.insert(0, ROOT_DIR)


def main():
    # ✅ Initialisation du logger
    debug = True  # tu pourras passer à False ou lire ça depuis ta config
    logger = setup_logger(debug=debug)
    logger.info("Démarrage de Vølund (main.py)")

    # ✅ Initialisation du dossier user_data
    try:
        user_data.init()
        logger.info("user_data initialisé avec succès")
    except Exception as e:
        logger.exception("Erreur lors de l'initialisation de user_data")

    # ✅ Lancement de l'application Qt
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        logger.info("Fenêtre principale affichée")
        sys.exit(app.exec())
    except Exception as e:
        logger.exception("Erreur critique lors du lancement de l'application")


if __name__ == "__main__":
    main()
