# modules/parlia/services/parlia_data.py

from core.user_data_manager import user_data

MODULE_NAME = "parlia"

KEY_MAX_DURATION = "max_duration"
KEY_MODEL_NAME = "model"
KEY_MODEL_FOLDER = "model_folder_path"
KEY_INCLUDE_CONCLUSION = "include_conclusion"
KEY_CONCLUSION_TEXT = "conclusion_text"


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
