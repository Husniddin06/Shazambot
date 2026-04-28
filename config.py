import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    # Eslatma: Bu xato botni ishga tushirishda ko'rinadi
    pass

ADMIN_ID = int(os.getenv("ADMIN_ID") or 0)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
SHAZAM_API_KEY = os.getenv("SHAZAM_API_KEY")
