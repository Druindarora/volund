# main_window.py

import importlib
import io
import os
import sys

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QVBoxLayout, QWidget

from core.window_config import load_window_state, save_window_state
from gui.home_screen import HomeScreen
from gui.sidebar import Sidebar
from utils.dev_state import load_last_module, save_last_module


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self._init_window()

        self._create_sidebar()
        self._create_content_area()
        self._create_home()

        # Récupération du dernier module actif (dev only)
        last = load_last_module()
        if last:
            self.handle_sidebar_click(last)

        self.sidebar.refresh()
        self.home_screen.module_favorited.connect(self.handle_favorite_toggle)

        self.central_widget.setLayout(self.main_layout)

    def _init_window(self):
        self.setWindowTitle("Vølund")
        icon_path = os.path.join("assets/icons/", "volund.ico")
        self.setWindowIcon(QIcon(icon_path))

        state = load_window_state()
        self.resize(state["width"], state["height"])
        self.move(state["x"], state["y"])
        self.setStyleSheet(load_qss("assets/styles/default.qss"))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self._save_timer = QTimer()
        self._save_timer.setInterval(1000)
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self._save_window_state)

    def _create_sidebar(self):
        self.sidebar = Sidebar(on_module_clicked=self.handle_sidebar_click)
        self.main_layout.addWidget(self.sidebar)

    def _create_content_area(self):
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_area.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content_area)

    def _create_home(self):
        self.home_screen = HomeScreen(main_window=self)
        self.content_layout.addWidget(self.home_screen)

    def handle_favorite_toggle(self, module_name: str, is_favorite: bool):
        self.sidebar.update_favorites()

    def handle_sidebar_click(self, module_name: str):
        # Nettoyer la zone centrale
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                if hasattr(widget, "cleanup"):
                    widget.cleanup()  # type: ignore[attr-defined]
                widget.setParent(None)
                widget.deleteLater()

        # Charger le bon module via un switch
        self._load_module(module_name)
        # Enregistrez le module courant (dev only)
        save_last_module(module_name)

    def _load_module(self, module_name: str):
        """
        Charge dynamiquement le module demandé, en appelant sa fonction `launch(parent)` si disponible.
        """
        if module_name == "home":
            self._create_home()
            return

        try:
            # Import dynamique du module Python depuis src.modules
            full_module_path = f"modules.{module_name}"
            mod = importlib.import_module(full_module_path)

            # Vérifie la présence de la fonction launch(parent)
            if hasattr(mod, "launch"):
                widget = mod.launch(parent=self)
                if widget is not None:
                    self.content_layout.addWidget(widget)
                    return

            print(
                f"⚠️ Le module '{module_name}' ne contient pas de fonction launch valide."
            )

        except ModuleNotFoundError:
            print(f"❌ Module introuvable : {module_name}")
        except Exception as e:
            print(f"❌ Erreur lors du chargement du module '{module_name}' : {e}")

    def closeEvent(self, event):
        self._save_window_state()
        super().closeEvent(event)

    def _save_window_state(self):
        x = self.x()
        y = self.y()
        width = self.width()
        height = self.height()
        save_window_state(x, y, width, height)

    def resizeEvent(self, event):
        self._save_timer.start()
        super().resizeEvent(event)

    def moveEvent(self, event):
        self._save_timer.start()
        super().moveEvent(event)


def load_qss(path: str) -> str:
    with open(path, "r") as file:
        return file.read()
