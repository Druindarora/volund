import os

from PySide6.QtCore import QSize, Qt
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
from utils.settings import Settings


class HomeScreen(QWidget):
    def __init__(self):
        super().__init__()
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
        # Appelle la méthode générique avec des valeurs fixes
        card = self.create_module_card(
            name="Vølund",
            icon_path=Settings.IMG_IN_PROGRESS,
            description="Ta prochaine application...",
            is_special=True,
        )
        self.grid_layout.addWidget(card, 0, 0)

    def populate_modules_from_manager(self):
        manager = ModuleManager()
        manager.load_modules()
        modules = manager.get_all_modules()

        row, col = 0, 1
        for module in modules:
            card = self.create_module_card(
                name=module.name,
                icon_path=module.icon_path,
                description=module.description,
            )
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

    def create_module_card(
        self, name: str, icon_path: str, description: str, is_special: bool = False
    ) -> QFrame:
        card = QFrame()
        card.setFixedSize(200, 200)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Étoile ---
        star_widget = self.build_star_widget(is_special)
        layout.addWidget(star_widget, alignment=Qt.AlignmentFlag.AlignRight)

        # --- Titre ---
        title_label = self.build_title_widget(name)
        layout.addWidget(title_label)

        # --- Icône ---
        icon_label = self.build_icon_widget(icon_path)
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # --- Description ---
        desc_label = self.build_description_widget(description)
        layout.addWidget(desc_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        card.setLayout(layout)
        card.setObjectName("cardStyle")

        return card

    def build_star_widget(self, is_special: bool) -> QWidget:
        if is_special:
            # Étoile statique pleine (ex : carte Vølund)
            label = QLabel()
            pixmap = QPixmap(Settings.FULL_STAR_PNG).scaled(
                16,
                16,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignmentFlag.AlignRight)
            return label
        else:
            # Étoile interactive (favori)
            button = QPushButton()
            button.setCheckable(True)
            button.setChecked(False)  # plus tard : à relier à une config utilisateur
            button.setMaximumWidth(30)
            button.setStyleSheet("border: none;")

            def update_icon():
                icon_path = (
                    Settings.FULL_STAR_PNG
                    if button.isChecked()
                    else Settings.EMPTY_STAR_PNG
                )
                button.setIcon(QIcon(icon_path))
                button.setIconSize(QSize(16, 16))

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
