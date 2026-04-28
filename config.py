import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    # This will be handled in main.py
    pass

ADMIN_ID = int(os.getenv("ADMIN_ID") or 0)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# New settings from Pasted_content_16.txt
SPONSOR_CHANNELS: list[str] = []
MAX_FILE_SIZE_MB = 50
PREMIUM_DAYS = 30
RATE_LIMIT_REQUESTS = 3
RATE_LIMIT_WINDOW = 5
