import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
