import os

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.module_manager import ModuleManager
from models.module_info import ModuleInfo
from utils.module_state import set_module_favorite
from utils.settings import Settings


class ClickableFrame(QFrame):
    clicked = Signal()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.clicked.emit()


class HomeScreen(QWidget):
    # Ajout du signal pour les favoris
    module_favorited = Signal(str, bool)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_layout()
        self.add_static_cards()
        self.populate_modules_from_manager()

    def setup_layout(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 60, 20, 20)

        # Titre centré en haut
        title_label = QLabel(Settings.LABEL_HOME)
        title_label.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )
        title_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title_label.setContentsMargins(0, 0, 0, 40)
        main_layout.addWidget(title_label)

        # Layout englobant la grille pour la centrer horizontalement
        grid_wrapper = QHBoxLayout()
        grid_wrapper.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(20)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        grid_wrapper.addLayout(self.grid_layout)
        main_layout.addLayout(grid_wrapper)

        main_layout.addStretch()
        self.setLayout(main_layout)

    def add_static_cards(self):
        # Création d'un module fictif pour la carte spéciale "Vølund"
        volund_module = ModuleInfo(
            name="Vølund",
            icon_path=Settings.IMG_IN_PROGRESS,
            description="Ta prochaine application...",
            favorite=True,
        )
        card = self.create_module_card(volund_module)
        self.grid_layout.addWidget(card, 0, 0)

    def populate_modules_from_manager(self):
        """Récupère les modules et les ajoute à la grille."""
        modules = self._get_modules_from_manager()
        self._add_modules_to_grid(modules)

    def _get_modules_from_manager(self):
        """Récupère les modules depuis le gestionnaire."""
        manager = ModuleManager()
        manager.load_modules()
        return manager.get_all_modules()

    def _add_modules_to_grid(self, modules):
        """Ajoute les modules à la grille."""
        row, col = 0, 1
        for module in modules:
            card = self.create_module_card(module)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

    def create_module_card(self, module):
        card = self._create_clickable_frame()
        layout = self._configure_card_layout(card)

        # Ajouter les widgets au layout
        self._add_star_widget(layout, module)
        self._add_title_widget(layout, module)
        self._add_icon_widget(layout, module)
        self._add_description_widget(layout, module)

        # Connecter les signaux spécifiques
        self._connect_signals(card, module)
        card.setObjectName("cardStyle")
        return card

    def _create_clickable_frame(self):
        """Crée un ClickableFrame pour un module."""
        card = ClickableFrame()
        card.setFixedSize(200, 200)
        return card

    def _configure_card_layout(self, card):
        """Configure le layout vertical pour un ClickableFrame."""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        card.setLayout(layout)
        return layout

    def _add_star_widget(self, layout, module):
        """Ajoute le widget étoile au layout."""
        star_widget = self.build_star_widget(module.name, module.favorite)
        layout.addWidget(star_widget, alignment=Qt.AlignmentFlag.AlignRight)

    def _add_title_widget(self, layout, module):
        """Ajoute le widget titre au layout."""
        title_label = self.build_title_widget(module.name)
        layout.addWidget(title_label)

    def _add_icon_widget(self, layout, module):
        """Ajoute le widget icône au layout."""
        icon_label = self.build_icon_widget(module.icon_path)
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignHCenter)

    def _add_description_widget(self, layout, module):
        """Ajoute le widget description au layout."""
        desc_label = self.build_description_widget(module.description)
        layout.addWidget(desc_label, alignment=Qt.AlignmentFlag.AlignHCenter)

    def _connect_signals(self, card, module):
        # Connecte dynamiquement TOUS les modules à handle_sidebar_click
        card.clicked.connect(
            lambda name=module.name.lower(): self.main_window.handle_sidebar_click(name)
        )

    def build_star_widget(self, module_name: str, default_fav: bool) -> QWidget:
        button = QPushButton()
        button.setCheckable(True)
        button.setChecked(default_fav)  # État initial basé sur le favori par défaut
        button.setMaximumWidth(30)
        button.setStyleSheet("border: none;")

        if module_name == "Vølund":
            button.setChecked(True)
            button.setEnabled(False)

        def update_icon():
            is_fav = button.isChecked()
            icon_path = Settings.FULL_STAR_PNG if is_fav else Settings.EMPTY_STAR_PNG
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(16, 16))
            # Sauvegarde l'état du favori dans le fichier JSON
            set_module_favorite(module_name, is_fav)
            # Émet le signal avec le nom du module et l'état de favori
            self.module_favorited.emit(module_name, is_fav)

        # Initialisation + signal
        update_icon()
        button.clicked.connect(update_icon)

        return button

    def build_title_widget(self, name: str) -> QLabel:
        # Vérifie si le nom est vide ou uniquement composé d'espaces
        clean_name = name.strip() if name else ""
        if not clean_name:
            clean_name = Settings.LABEL_NO_TITLE

        title = QLabel(clean_name)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        return title

    def build_icon_widget(self, icon_path: str) -> QLabel:
        icon = QLabel()
        icon.setFixedSize(80, 80)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if not os.path.exists(icon_path) or not os.path.isfile(icon_path):
            icon_path = Settings.DEFAULT_IMAGE_PNG

        # Charge et scale l’image avec marges si nécessaire
        pixmap = QPixmap(icon_path).scaled(
            70,
            70,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        icon.setPixmap(pixmap)

        return icon

    def build_description_widget(self, description: str) -> QLabel:
        fallback = Settings.LABEL_NO_DESCRIPTION
        clean_desc = description.strip() if description else ""
        if not clean_desc:
            clean_desc = fallback

        # Troncature manuelle + points de suspension
        max_chars = 100
        if len(clean_desc) > max_chars:
            clean_desc = clean_desc[: max_chars - 3].rstrip() + "..."

        desc = QLabel(clean_desc)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        desc.setFixedWidth(160)
        return desc
