# 📄 Page d’accueil du module Parlia
# Créer une fonction `createParliaHome(main_window: QMainWindow)` qui renvoie un QWidget
# Ce QWidget contiendra simplement un QLabel avec le texte "Bienvenue dans Parlia"
# Utiliser une mise en page verticale centrée (QVBoxLayout)
# Ce composant doit pouvoir être affiché dans le `centralWidget` de MainWindow

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget


def createParliaHome(main_window: QMainWindow) -> QWidget:
    # Créer un widget principal
    parlia_home_widget = QWidget(main_window)

    # Créer un QLabel avec le texte "Bienvenue dans Parlia"
    label = QLabel("Bienvenue dans Parlia", parlia_home_widget)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # Configurer une mise en page verticale
    layout = QVBoxLayout()
    layout.addWidget(label)

    # Appliquer la mise en page au widget
    parlia_home_widget.setLayout(layout)

    return parlia_home_widget
