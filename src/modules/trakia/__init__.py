# __init__.py – Métadonnées du module Trakia

from PySide6.QtWidgets import QWidget

from models.module_info import ModuleInfo as BaseModuleInfo
from modules.trakia.ui.home_panel import HomePanel

# Trakia observe et enregistre discrètement tes interactions IA. Il compte, il mesure, il sait. Garde un œil sur ta limite... ou sur toi-même.

name = "Trakia"
version = "0.1.0"
description = "Le traqueur silencieux de tes échanges IA"
icon_path = "assets/images/trakia.png"
tags = []
favorite = False
mobile = False
path = ""


def launch(parent=None) -> QWidget:
    # Fonction à implémenter : retourne un QWidget pour lancer le module
    return HomePanel()


ModuleInfo = BaseModuleInfo(
    name=name,
    version=version,
    description=description,
    icon_path=icon_path,
    tags=tags,
    favorite=favorite,
    mobile=mobile,
    path=path,
)
