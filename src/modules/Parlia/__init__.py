# __init__.py – Métadonnées du module Parlia

from models.module_info import ModuleInfo as BaseModuleInfo

name = 'Parlia'
version = '0.1.0'
description = ''
icon_path = 'assets/images/parlia.png'
tags = []
favorite = False
mobile = False
path = ''


def launch(parent=None):
    # Fonction à implémenter : retourne un QWidget pour lancer le module
    return None

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
