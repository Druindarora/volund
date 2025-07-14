import sys

from PySide6.QtWidgets import QApplication

from core.user_data_manager import user_data
from gui.main_window import MainWindow


def main():
    # ✅ Initialisation du dossier / fichiers user_data/
    user_data.init()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
