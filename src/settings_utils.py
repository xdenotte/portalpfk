import json
import os

SETTINGS_FILE = "settings.json"

# Функція для завантаження налаштувань
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as file:
            return json.load(file)
    return {"theme_mode": "Системна"}  # Значення за замовчуванням

# Функція для збереження налаштувань
def save_settings(settings):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file)
