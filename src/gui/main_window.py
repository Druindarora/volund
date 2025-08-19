import importlib
import io
import os
import sys

from core.logger_manager import get_logger
from core.window_config import load_window_state, save_window_state

logger = get_logger("MainWindow")

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from PySide6.QtCore import QEvent, QTimer
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QWidget,
)

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

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        state = load_window_state()

        # Trouver l'écran demandé
        target_screen = None
        if state.get("screen"):
            for s in QGuiApplication.screens():
                if s.name() == state["screen"]:
                    target_screen = s
                    break

        def show_on_screen():
            if self.windowHandle() and target_screen:
                self.windowHandle().setScreen(target_screen)
            if state.get("maximized", True):
                self.showMaximized()
            else:
                self.showNormal()

        QTimer.singleShot(0, show_on_screen)

        self.setStyleSheet(load_qss("assets/styles/default.qss"))

    def _create_sidebar(self):
        self.sidebar = Sidebar(on_module_clicked=self.handle_sidebar_click)
        self.sidebar.restart_button.clicked.connect(self.restart_app)
        self.main_layout.addWidget(self.sidebar)

    def _create_content_area(self):
        self.content_area = QStackedWidget()
        self.content_area.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.main_layout.addWidget(self.content_area)

    def _create_home(self):
        self.home_screen = HomeScreen(main_window=self)
        setattr(self.home_screen, "module_name", "home")
        self.home_screen.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.content_area.addWidget(self.home_screen)
        self.content_area.setCurrentWidget(self.home_screen)

    def handle_favorite_toggle(self, module_name: str, is_favorite: bool):
        self.sidebar.update_favorites()

    def handle_sidebar_click(self, module_name: str):
        # Vérifier si déjà présent
        for i in range(self.content_area.count()):
            widget = self.content_area.widget(i)
            if getattr(widget, "module_name", None) == module_name:
                self.content_area.setCurrentWidget(widget)
                save_last_module(module_name)
                return

        # Sinon, charger le module
        widget = self._load_module(module_name)
        if widget:
            setattr(widget, "module_name", module_name)

            # Vérifier si le contenu dépasse l'espace dispo
            available = self.content_area.size()
            if (
                widget.sizeHint().height() > available.height()
                or widget.sizeHint().width() > available.width()
            ):
                scroll = QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setWidget(widget)
                setattr(scroll, "module_name", module_name)
                self.content_area.addWidget(scroll)
                self.content_area.setCurrentWidget(scroll)
            else:
                widget.setSizePolicy(
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
                )
                self.content_area.addWidget(widget)
                self.content_area.setCurrentWidget(widget)

            save_last_module(module_name)

    def _load_module(self, module_name: str):
        logger.info(f"[_load_module] Tentative de chargement : {module_name}")

        if module_name == "home":
            widget = HomeScreen(main_window=self)
            setattr(widget, "module_name", "home")
            logger.info("[_load_module] HomeScreen instancié avec succès")
            return widget

        # ⬇️ remplacer le try par cette version
        try:
            normalized = module_name.lower()  # normalise pour Linux
            full_module_path = f"modules.{normalized}"
            logger.info(f"[_load_module] importlib -> {full_module_path}")
            mod = importlib.import_module(full_module_path)
            logger.info("[_load_module] Import réussi")

            if hasattr(mod, "launch"):
                widget = mod.launch(parent=self)
                if widget is None:
                    logger.error(f"[_load_module] launch() de {module_name} a renvoyé None")
                else:
                    setattr(widget, "module_name", module_name)
                    logger.info(f"[_load_module] Widget {module_name} instancié : {widget}")
                return widget

            logger.error(f"[_load_module] Pas de fonction launch() dans {module_name}")

        except Exception as e:
            logger.exception(
                f"[_load_module] Erreur lors du chargement de {module_name}: {e}"
            )

        return None

    def restart_app(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def closeEvent(self, event):
        maximized = self.isMaximized()
        screen_name = None
        if self.windowHandle() and self.windowHandle().screen():
            screen_name = self.windowHandle().screen().name()

        save_window_state(maximized=maximized, screen=screen_name)
        super().closeEvent(event)

    def moveEvent(self, event):
        maximized = self.isMaximized()
        screen_name = None
        if self.windowHandle() and self.windowHandle().screen():
            screen_name = self.windowHandle().screen().name()

        save_window_state(maximized=maximized, screen=screen_name)
        super().moveEvent(event)

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            maximized = self.isMaximized()
            screen_name = None
            if self.windowHandle() and self.windowHandle().screen():
                screen_name = self.windowHandle().screen().name()
            save_window_state(maximized=maximized, screen=screen_name)
        super().changeEvent(event)


def load_qss(path: str) -> str:
    with open(path, "r") as file:
        return file.read()
