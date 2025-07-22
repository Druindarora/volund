# env.py — gestion de l'environnement de l'application
from utils.settings import Settings


def is_dev() -> bool:
    return Settings.ENV == "dev"


def is_prod() -> bool:
    return Settings.ENV == "prod"


def is_test() -> bool:
    return Settings.ENV == "test"
