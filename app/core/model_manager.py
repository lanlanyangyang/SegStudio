import os
import json

from config.settings import CONFIG_DIR, CONFIG_FILE, MODELS_FOLDER

def _load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def get_current_model_path():
    config = _load_config()
    path = config.get("current_model_path")
    if path and os.path.exists(path):
        return path
    from config.settings import MODEL_PATH
    return MODEL_PATH

def set_current_model_path(path):
    config = _load_config()
    config["current_model_path"] = path
    _save_config(config)

def list_available_models():
    if not os.path.exists(MODELS_FOLDER):
        return []
    files = [f for f in os.listdir(MODELS_FOLDER) if f.lower().endswith((".pth", ".pt"))]
    return [os.path.join(MODELS_FOLDER, f) for f in files]