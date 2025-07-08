# main_window.py

# Fenêtre principale de l'application Volund
# Utilise PySide6 uniquement
# Affiche une Sidebar à gauche, et une zone centrale à droite
# La position et la taille de la fenêtre sont restaurées automatiquement
# L’état est sauvegardé en différé lorsqu’on déplace ou redimensionne la fenêtre

import io
import os
import sys

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QWidget

from core.window_config import load_window_state, save_window_state
from gui.home_screen import HomeScreen
from gui.sidebar import Sidebar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialisation complète de la fenêtre
        self._init_window()

        # Construction des éléments d’interface
        self._create_sidebar()
        self._create_home()
        self.sidebar.refresh()

        # Connecter le signal des favoris
        self.home_screen.module_favorited.connect(self.handle_favorite_toggle)

        # Appliquer le layout final
        self.central_widget.setLayout(self.main_layout)

    def _init_window(self):
        """
        Initialise la fenêtre principale :
        - Titre, position, taille
        - Widget central + layout horizontal
        - Timer de sauvegarde intelligente
        """
        self.setWindowTitle("Vølund")

        # Définir l'icône (Windows .ico)
        icon_path = os.path.join("assets/icons/", "volund.ico")
        self.setWindowIcon(QIcon(icon_path))

        # Charger la configuration sauvegardée
        state = load_window_state()
        self.resize(state["width"], state["height"])
        self.move(state["x"], state["y"])
        self.setStyleSheet(load_qss("assets/styles/default.qss"))
        # Créer le widget central et le layout horizontal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Timer différé pour éviter les sauvegardes répétées
        self._save_timer = QTimer()
        self._save_timer.setInterval(1000)  # 1 seconde
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self._save_window_state)

    def _create_sidebar(self):
        """
        Crée et ajoute la Sidebar à gauche dans le layout principal.
        """
        self.sidebar = Sidebar()
        self.main_layout.addWidget(self.sidebar)

    def _create_home(self):
        """
        Crée et ajoute la zone centrale (accueil, modules...) à droite.
        Pour l’instant, simple fond sombre en placeholder.
        """
        # self.content_area = QWidget()
        # self.content_area.setStyleSheet("background-color: #1e1e1e;")
        # self.main_layout.addWidget(self.content_area)
        self.home_screen = HomeScreen()
        # Ajouter la page d’accueil au layout principal
        self.main_layout.addWidget(self.home_screen)

    def closeEvent(self, event):
        """
        Sauvegarde l’état de la fenêtre (taille + position) à la fermeture.
        """
        self._save_window_state()
        super().closeEvent(event)

    def _save_window_state(self):
        x = self.x()
        y = self.y()
        width = self.width()
        height = self.height()
        save_window_state(x, y, width, height)

    def resizeEvent(self, event):
        """
        Déclenche une sauvegarde différée si la taille change.
        """
        self._save_timer.start()
        super().resizeEvent(event)

    def moveEvent(self, event):
        """
        Déclenche une sauvegarde différée si la position change.
        """
        self._save_timer.start()
        super().moveEvent(event)

    def handle_favorite_toggle(self, module_name: str, is_favorite: bool):
        """
        Gère les changements d'état de favori d'un module.
        """
        self.sidebar.update_favorites()


def load_qss(path: str) -> str:
    with open(path, "r") as file:
        return file.read()
