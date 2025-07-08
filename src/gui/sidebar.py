from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout

from core.module_manager import ModuleManager
from gui.images_paths import ICONS


class Sidebar(QFrame):
    def __init__(self, on_module_clicked=None, parent=None):
        super().__init__(parent)
        self.on_module_clicked = on_module_clicked

        # Initialisation des propriétés de base
        self._initialize_properties()

        # Création des boutons principaux
        self._create_main_buttons()

        # Configuration de la zone des favoris
        self._setup_favorites_area()

        # Configuration du layout principal
        self._setup_main_layout()

    def _initialize_properties(self):
        """Initialise les propriétés de base de la Sidebar."""
        self.setFixedWidth(50)
        self.setObjectName("Sidebar")

    def _create_main_buttons(self):
        """Crée les boutons principaux (Home et Settings)."""
        self.home_button = QPushButton()
        if callable(self.on_module_clicked):
            self.home_button.clicked.connect(lambda: self.on_module_clicked("home"))  # type: ignore

        self.home_button.setIcon(QIcon(ICONS["home"]))
        self.home_button.setIconSize(QSize(35, 35))
        self.home_button.setFixedSize(40, 40)

        self.settings_button = QPushButton()
        self.settings_button.setIcon(QIcon(ICONS["settings"]))
        self.settings_button.setIconSize(QSize(30, 30))
        self.settings_button.setFixedSize(40, 40)

    def _setup_favorites_area(self):
        """Configure la zone des favoris."""
        self.favorites_layout = QVBoxLayout()
        self.favorites_layout.setContentsMargins(0, 0, 0, 0)
        self.favorites_layout.setSpacing(0)

        self.favorites_container = QFrame()
        self.favorites_container.setObjectName("FavoritesContainer")
        self.favorites_container.setContentsMargins(0, 0, 0, 0)
        self.favorites_container.setStyleSheet("background: transparent;")
        self.favorites_container.setLayout(self.favorites_layout)

    def _setup_main_layout(self):
        """Configure le layout principal de la Sidebar."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Ajouter le bouton Home en haut
        layout.addWidget(self.home_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Ajouter la zone des favoris
        layout.insertWidget(
            1, self.favorites_container, alignment=Qt.AlignmentFlag.AlignTop
        )

        # Ajouter un stretch pour pousser le reste en bas
        layout.addStretch()

        # Ajouter le bouton Settings en bas
        layout.addWidget(self.settings_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Appliquer le layout à la Sidebar
        self.setLayout(layout)

    def get_buttons(self):
        return {"home": self.home_button, "settings": self.settings_button}

    def update_favorites(self):
        self.refresh()

    def refresh(self):
        """Met à jour la liste des favoris dans la Sidebar."""
        self._clear_favorites()
        favorite_modules = self._load_favorite_modules()
        self._populate_favorites(favorite_modules)

    def _clear_favorites(self):
        """Vide la zone des favoris."""
        while self.favorites_layout.count():
            item = self.favorites_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _load_favorite_modules(self):
        """Charge les modules favoris depuis le gestionnaire."""
        manager = ModuleManager()
        manager.load_modules()
        return [m for m in manager.get_all_modules() if m.favorite]

    def _populate_favorites(self, favorite_modules):
        """Ajoute les boutons des modules favoris à la zone des favoris."""
        for module in favorite_modules:
            button = self._create_favorite_button(module)
            self.favorites_layout.addWidget(
                button, alignment=Qt.AlignmentFlag.AlignHCenter
            )

    def _create_favorite_button(self, module):
        """Crée un bouton pour un module favori."""
        button = QPushButton()
        button.setIcon(QIcon(module.icon_path))
        button.setIconSize(QSize(30, 30))
        button.setFixedSize(40, 40)
        button.setToolTip(module.name)

        # Connecter le clic du bouton au callback si défini
        if callable(self.on_module_clicked):
            button.clicked.connect(
                lambda _, name=module.name.lower(): self.on_module_clicked(name)  # type: ignore
            )

        return button
