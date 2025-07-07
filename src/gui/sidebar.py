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
        layout.addWidget(self.home_button, alignment=Qt.AlignHCenter)

        # Ajouter un stretch pour pousser le reste en bas
        layout.addStretch()

        # Ajouter le bouton Settings en bas
        self.settings_button = QPushButton()
        self.settings_button.setIcon(QIcon(ICONS["settings"]))
        self.settings_button.setIconSize(QSize(30, 30))
        self.settings_button.setFixedSize(40, 40)
        layout.addWidget(self.settings_button, alignment=Qt.AlignHCenter)

        # Appliquer le layout à la Sidebar
        self.setObjectName("Sidebar")
        self.setLayout(layout)

    def get_buttons(self):
        return {"home": self.home_button, "settings": self.settings_button}
