import json

from config import LANGUAGES
from database import Database

db = Database()

def load_translations():
    translations = {}
    for lang in LANGUAGES:
        with open(f"languages/{lang}.json", "r", encoding="utf-8") as file:
            translations[lang] = json.load(file)
    return translations

TRANSLATIONS = load_translations()

def get_translation(key, language="uz"):
    return TRANSLATIONS.get(language, {}).get(key, key)

def get_user_language(user_id):
    user_data = db.get_user(user_id)
    return user_data[4] if user_data else "uz"
