import json
import os

DEFAULT_SETTINGS = {"theme_mode": "Системна"}
SETTINGS_FILE = "settings.json"


def _settings_path() -> str:
    base_dir = os.environ.get("FLET_APP_STORAGE_DATA") or os.path.expanduser("~")
    return os.path.join(base_dir, SETTINGS_FILE)


def load_settings() -> dict:
    path = _settings_path()
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return dict(DEFAULT_SETTINGS)

    return {**DEFAULT_SETTINGS, **data}


def save_settings(settings: dict) -> None:
    path = _settings_path()
    try:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(settings, file, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"[ERROR] Не вдалося зберегти налаштування: {e}")
