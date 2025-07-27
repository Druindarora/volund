# === FICHIER : config.py (modules/parlia/) ===
# 🔍 Audit du fichier de configuration central de Parlia
# --------------------------------------------------
# ✅ Rôle : stocker les constantes (hotkey, délais, messages) de manière structurée
# --------------------------------------------------

# ✅ Points positifs :
# - Organisation propre avec classes imbriquées (`Timeouts`, `ParliaConfig`)
# - Accès typé et structuré : `config.timeouts.paste_delay`, etc.
# - Instance globale unique (`config`) bien nommée

# 🛠 Recommandations d’évolution :
# 1. 📦 Déplacer ce fichier dans `modules/parlia/core/` ou `config/` si tu veux une vraie centralisation future
# 2. 🔁 Ajouter une méthode `as_dict()` (utile pour tests / UI avancées / export)
# 3. 🔄 Ajouter d’autres groupes : `CursorConfig`, `CodellamaConfig`, `LoggerConfig`, etc.
# 4. 🧪 Prévoir un jour un chargement dynamique depuis un fichier (ex : `config.yaml`)

# ✅ À garder absolument pour la suite, avec évolution vers un vrai "hub de settings constants"


class Timeouts:
    @property
    def window_switch(self) -> float:
        return 0.5

    @property
    def text_input(self) -> float:
        return 0.1

    @property
    def paste_delay(self) -> float:
        return 0.4

    @property
    def after_paste_delay(self) -> float:
        return 1.0


class ParliaConfig:
    @property
    def hotkey(self) -> str:
        return "ctrl+shift+f12"

    @property
    def focus_countdown(self) -> int:
        return 5

    @property
    def timeouts(self) -> Timeouts:
        return Timeouts()

    @property
    def vscode_window_title(self) -> str:
        return "Visual Studio Code"

    @property
    def default_countdown_message(self) -> str:
        return "Attention, vous avez {n} seconde(s) pour vous focus sur VS Code..."


# ✅ L’instance typée
config = ParliaConfig()
