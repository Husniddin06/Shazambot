import os
from dotenv import load_dotenv

load_dotenv()

# Bot sozlamalari
BOT_TOKEN = os.getenv("BOT_TOKEN", "7810588142:AAGBNgggP3KTpN1lQ5MCQRZx7WHfc-fk9rA")
ADMIN_ID = int(os.getenv("ADMIN_ID", 1999635628))
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# API Keys
YOUTUBE_API = os.getenv("YOUTUBE_API")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_SECRET = os.getenv("SPOTIFY_SECRET")
SHAZAM_API_KEY = os.getenv("SHAZAM_API_KEY")
