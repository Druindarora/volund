# === FICHIER : parlia_data.py ===
# 🔍 Audit et consolidation des données persistantes Parlia
# --------------------------------------------------
# ✅ Ce fichier agit comme interface entre le module Parlia et `user_data_manager`
# 📁 Sa place est légitime dans `services/` pour l’instant
# 🔧 Il regroupe :
#   - des préférences utilisateur (durée, modèle Whisper, prompts...)
#   - des flags simples (conclusion activée, etc.)
#   - des labels associés aux prompts
# --------------------------------------------------

# ✅ Pas de refactor nécessaire à ce stade
# 🔄 Plus tard : possibilité de splitter en :
#     - user_preferences.py (durée, modèle, dossier...)
#     - prompt_config.py (tous les prompts + labels)
#     - settings_schema.json (future validation ?)

# 🚩 À surveiller si le fichier devient trop long ou contient trop de types de données différentes


from core.user_data_manager import user_data

MODULE_NAME = "parlia"

KEY_MAX_DURATION = "max_duration"
KEY_MODEL_NAME = "model"
KEY_MODEL_FOLDER = "model_folder_path"
KEY_INCLUDE_CONCLUSION = "include_conclusion"
KEY_CONCLUSION_TEXT = "conclusion_text"
KEY_PROMPT_CODE_VS_CODE = "prompt_code_vs_code"

PROMPT_DEFINITIONS = {
    "prompt_code_comments": "Code les commentaires (focus VS Code et code)",
    "prompt_refactor": "Refactorise ce code proprement",
    "prompt_explain": "Explique ce code ligne par ligne",
    "prompt_analyze": "Analyse les erreurs potentielles de ce code",
    "prompt_generate_tests": "Génère des tests pour ce code",
}


def get_max_duration() -> int:
    value = user_data.get(MODULE_NAME, KEY_MAX_DURATION)
    if isinstance(value, str) and value.isdigit():
        return int(value)
    if isinstance(value, int):
        return value
    return 0


def set_max_duration(value: int):
    user_data.set(MODULE_NAME, KEY_MAX_DURATION, int(value))


def get_model_name() -> str:
    value = user_data.get(MODULE_NAME, KEY_MODEL_NAME)
    return value if isinstance(value, str) else "tiny"


def set_model_name(name: str):
    user_data.set(MODULE_NAME, KEY_MODEL_NAME, name)


def get_model_folder_path() -> str:
    value = user_data.get(MODULE_NAME, KEY_MODEL_FOLDER)
    return value if isinstance(value, str) else ""


def set_model_folder_path(path: str):
    user_data.set(MODULE_NAME, KEY_MODEL_FOLDER, path)


def get_include_conclusion() -> bool:
    value = user_data.get(MODULE_NAME, KEY_INCLUDE_CONCLUSION)
    return bool(value)


def set_include_conclusion(enabled: bool):
    user_data.set(MODULE_NAME, KEY_INCLUDE_CONCLUSION, enabled)


def get_conclusion_text() -> str:
    value = user_data.get(MODULE_NAME, KEY_CONCLUSION_TEXT)
    return value if isinstance(value, str) else ""


def set_conclusion_text(text: str):
    user_data.set(MODULE_NAME, KEY_CONCLUSION_TEXT, text)


def set_prompt_code_vs_code(prompt: str):
    user_data.set(MODULE_NAME, KEY_PROMPT_CODE_VS_CODE, prompt)


def get_prompt(key: str) -> str:
    value = user_data.get(MODULE_NAME, key)
    if isinstance(value, str) and value.strip():
        return value
    return "Aucun prompt"


def set_prompt(key: str, prompt: str):
    user_data.set(MODULE_NAME, key, prompt)


def get_prompt_label(key: str) -> str:
    return PROMPT_DEFINITIONS.get(key, key)
