# sidebar.py

# Ce fichier définit une Sidebar verticale minimaliste pour l'application Vølund.
# L'interface est développée avec **PySide6 uniquement** (pas PyQt5 ni PyQt6).
# Il ne faut **importer que depuis PySide6**, sans dépendances tierces.

# 🧱 Objectif :
# Créer une classe Sidebar basée sur QFrame, affichée à gauche de la fenêtre principale.
# Elle contient :
# - un bouton "home" (🏠) en haut
# - une zone centrale vide pour les futurs modules favoris
# - un bouton "settings" (⚙️) en bas

# 📐 Contraintes visuelles :
# - Disposition verticale avec QVBoxLayout
# - Largeur fixe réduite (50 px) pour ressembler à une barre latérale type IDE
# - Boutons centrés horizontalement
# - Un stretch vertical pour séparer le haut et le bas

# ✅ Comportement actuel :
# - Chaque bouton est un QPushButton avec un emoji comme texte
# - Le layout est sans marges ni espacement
# - Aucun signal n’est connecté pour l’instant (statique)

# 🎨 Style :
# - Fond gris foncé (`#2b2b2b`)
# - Bordure verticale droite (1px) en gris clair (`#666`)
# - Boutons blancs avec léger padding horizontal
# - Hover discret (`#3c3c3c`)
# - Le style est appliqué via un `objectName` (#Sidebar) pour cibler précisément le widget

# 🧩 Structure interne :
# - `self.home_button` (🏠) placé en haut
# - `layout.addStretch()` pour séparer visuellement
# - `self.settings_button` (⚙️) placé en bas
# - Accès possible via la méthode get_buttons()

# 📂 À venir :
# - Ajout dynamique des modules favoris dans la zone centrale
# - Gestion des états (actif, cliqué, badge)

# ⚠️ Ne pas utiliser PyQt5 ni PyQt6
# ⚠️ Ne pas importer de bibliothèques externes
# Le code doit rester simple, modulaire, et maintenable.


from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout

from core.module_manager import ModuleManager
from gui.images_paths import ICONS


class Sidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Définir la largeur fixe de la Sidebar
        self.setFixedWidth(50)

        # Créer le layout principal vertical
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Ajouter le bouton Home en haut
        self.home_button = QPushButton()
        self.home_button.setIcon(QIcon(ICONS["home"]))
        self.home_button.setIconSize(QSize(35, 35))
        self.home_button.setFixedSize(40, 40)
        layout.addWidget(self.home_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Zone centrale pour les favoris
        self.favorites_layout = QVBoxLayout()

        # Créer un widget conteneur pour les favoris
        self.favorites_container = QFrame()
        self.favorites_container.setObjectName("FavoritesContainer")
        self.favorites_container.setContentsMargins(0, 0, 0, 0)
        self.favorites_container.setStyleSheet("background: transparent;")

        self.favorites_layout = QVBoxLayout()
        self.favorites_layout.setContentsMargins(0, 0, 0, 0)
        self.favorites_layout.setSpacing(0)

        self.favorites_container.setLayout(self.favorites_layout)
        layout.insertWidget(
            1, self.favorites_container, alignment=Qt.AlignmentFlag.AlignTop
        )

        # Ajouter un stretch pour pousser le reste en bas
        layout.addStretch()

        # Ajouter le bouton Settings en bas
        self.settings_button = QPushButton()
        self.settings_button.setIcon(QIcon(ICONS["settings"]))
        self.settings_button.setIconSize(QSize(30, 30))
        self.settings_button.setFixedSize(40, 40)
        layout.addWidget(self.settings_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Appliquer le layout à la Sidebar
        self.setObjectName("Sidebar")
        self.setLayout(layout)

    def get_buttons(self):
        return {"home": self.home_button, "settings": self.settings_button}

    def update_favorites(self, module_name: str, is_favorite: bool):
        print(f"[Sidebar] Mise à jour : {module_name} -> favori={is_favorite}")
        self.refresh()

    def refresh(self):
        # Vider la zone des favoris
        while self.favorites_layout.count():
            item = self.favorites_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Recharger les modules favoris
        manager = ModuleManager()
        manager.load_modules()
        favorite_modules = [m for m in manager.get_all_modules() if m.favorite]

        for module in favorite_modules:
            button = QPushButton()
            button.setIcon(QIcon(module.icon_path))
            button.setIconSize(QSize(30, 30))
            button.setFixedSize(40, 40)
            button.setToolTip(module.name)
            self.favorites_layout.addWidget(
                button, alignment=Qt.AlignmentFlag.AlignHCenter
            )
