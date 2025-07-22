# modules/parlia/services/parlia_data.py

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


def get_max_duration() -> str:
    value = user_data.get(MODULE_NAME, KEY_MAX_DURATION)
    if isinstance(value, str) and value.isdigit():
        return value
    return "0"


def set_max_duration(seconds: int):
    user_data.set(MODULE_NAME, KEY_MAX_DURATION, seconds)


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
