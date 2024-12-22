import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
DB_PATH = os.getenv("DB_PATH", "bot_db.db")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
LANGUAGES = ['uz', 'ru', 'en']
