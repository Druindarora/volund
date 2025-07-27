# __init__.py – Métadonnées du module Parlia

from PySide6.QtWidgets import QWidget

from models.module_info import ModuleInfo as BaseModuleInfo

name = "Parlia"
version = "0.1.0"
description = ""
icon_path = "assets/images/parlia.png"
tags = []
favorite = False
mobile = False
path = ""


def launch(parent=None) -> QWidget:
    # ⚠️ Import déplacé ici pour éviter l'importation circulaire
    from modules.parlia.ui.home_parlia import ParliaHome

    return ParliaHome(main_window=parent)


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
