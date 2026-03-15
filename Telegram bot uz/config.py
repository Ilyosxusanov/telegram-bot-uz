import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
_admin_ids_raw = os.getenv("ADMIN_IDS", os.getenv("ADMIN_ID", ""))
ADMIN_IDS = [int(i.strip()) for i in _admin_ids_raw.split(",") if i.strip().isdigit()]

# Kanal sozlamalari
CHANNEL_ID = "@kino_4ksifada"
CHANNEL_LINK = "https://t.me/kino_4ksifada"

if not BOT_TOKEN:
    exit("Error: BOT_TOKEN not found in .env file")
