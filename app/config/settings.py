import json
import os
import sys

DEFAULT_ADMIN_PASSWORD = "123456"

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

APP_DIR = os.path.join(BASE_DIR, "app") if os.path.exists(os.path.join(BASE_DIR, "app")) else BASE_DIR
CONFIG_DIR = os.path.join(APP_DIR, "config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "model_config.json")
MODELS_FOLDER = os.path.join(BASE_DIR, "models")
DATA_DIR = os.path.join(BASE_DIR, "data")
AUTO_LABELED_DIR = os.path.join(DATA_DIR, "auto_labeled")
MANUAL_NOTES_DIR = os.path.join(DATA_DIR, "manual_notes")
PASSWORD_FILE = os.path.join(CONFIG_DIR, "admin_password.json")
MODEL_PATH = os.path.join(MODELS_FOLDER, "AI_Cells_Custom_V5_converted.pth")
DEFAULT_OUTPUT_MODEL_PATH = os.path.join(MODELS_FOLDER, "AI_Cells_Custom_V6.pth")


def _ensure_password_file():
    os.makedirs(os.path.dirname(PASSWORD_FILE), exist_ok=True)
    if not os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, "w", encoding="utf-8") as fh:
            json.dump({"password": DEFAULT_ADMIN_PASSWORD}, fh, ensure_ascii=False, indent=2)


def get_admin_password():
    _ensure_password_file()
    with open(PASSWORD_FILE, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("password", DEFAULT_ADMIN_PASSWORD)


def set_admin_password(new_password):
    _ensure_password_file()
    with open(PASSWORD_FILE, "w", encoding="utf-8") as fh:
        json.dump({"password": new_password}, fh, ensure_ascii=False, indent=2)


def is_admin_password_correct(password):
    return password == get_admin_password()