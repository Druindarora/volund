# services/macros/create_module_service.py

from __future__ import annotations

import base64
import logging
from pathlib import Path
from typing import Any, Dict, Final

from jinja2 import Environment, FileSystemLoader, TemplateNotFound  # ⬅️ NEW

# --- Logger de service ---
_logger = logging.getLogger("create_module")
if not _logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    _logger.addHandler(_h)
_logger.setLevel(logging.INFO)

# Répertoire des templates (UTF-8)
BASE_DIR: Final[Path] = Path(__file__).resolve().parents[2]
TEMPLATES_DIR: Final[Path] = BASE_DIR / "core" / "templates"

# ⬅️ NEW: environnement Jinja2 global (sans échappement, blocs nettoyés)
env: Environment = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True,
)

# PNG 1x1 transparent (placeholder image)
_ONE_BY_ONE_PNG_B64: Final[str] = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
)


def renderTemplate(templateName: str, context: Dict[str, Any]) -> str:
    """Rend un template .j2 via Jinja2."""
    try:
        tpl = env.get_template(templateName)
    except TemplateNotFound as exc:  # pragma: no cover
        raise FileNotFoundError(f"Template introuvable: {templateName}") from exc
    return tpl.render(context)


def _writeText(path: Path, content: str) -> None:
    """Écrit du texte UTF-8 en créant les dossiers au besoin."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _writeBinary(path: Path, data: bytes) -> None:
    """Écrit des données binaires en créant les dossiers au besoin."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def createModule(name: str, description: str = "", mobile: bool = False) -> bool:
    """
    Génère un module sous `src/modules/<name>` à partir de templates Jinja2.
    Retourne True si succès, False sinon (existant/erreur).
    """
    safeName = name.strip()
    if not safeName:
        _logger.error("Nom de module vide.")
        return False

    baseDir = Path("src") / "modules" / safeName
    if baseDir.exists():
        _logger.warning("Le module existe déjà: %s", baseDir)
        return False

    try:
        # 1) Dossiers
        for rel in [
            "core",
            "services",
            "ui",
            "ui/dialogs",
            "db",
            "tests",
            "assets/images",
            "assets/styles",
            "utils",
            "workers",
            "i18n",
            "spec",
        ]:
            (baseDir / rel).mkdir(parents=True, exist_ok=True)

        # 2) Contexte commun des templates
        context: Dict[str, Any] = {
            "name": safeName,
            "title": safeName.title(),
            "version": "0.1.0",
            "description": description,
            "favorite": False,
            "mobile": mobile,
        }

        # 3) Rendus des templates → fichiers (.j2)
        files_map: Dict[str, str] = {
            "__init__.py": "init_template.py.j2",
            "ui/home_panel.py": "home_panel_template.py.j2",
            "core/logger.py": "logger_template.py.j2",
            "utils/stylesheet_loader.py": "stylesheet_loader_template.py.j2",
            "tests/test_basic.py": "test_basic_template.py.j2",
            "README.md": "readme_template.md.j2",
            "services/module_data.py": "module_data.py.j2",
            "i18n/module_strings.py": "module_strings.py.j2",
        }

        for relDest, tplName in files_map.items():
            content = renderTemplate(tplName, context)  # ⬅️ Jinja2
            _writeText(baseDir / relDest, content)

        # 4) Placeholder image
        png_bytes = base64.b64decode(_ONE_BY_ONE_PNG_B64.encode("ascii"))
        _writeBinary(baseDir / "assets" / "images" / f"{safeName}.png", png_bytes)

        _logger.info("Module créé: %s", baseDir)
        return True
    except Exception as exc:
        _logger.error("Erreur création module '%s': %s", safeName, exc)
        return False
