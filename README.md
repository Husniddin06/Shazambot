# All-in-one Media Bot 🚀

Professional Telegram bot for downloading media from various platforms and music identification.

## Features 🌟

- 🎵 **Music Download**: YouTube to MP3, Spotify search.
- 🎬 **Video Download**: YouTube, TikTok (no watermark), Instagram Reels, VK.
- 🎤 **Voice ID**: Identify music via voice (Shazam API).
- ⚡ **Speed**: Redis caching and async processing.
- 👑 **Admin Panel**: Statistics and broadcasting.

## Tech Stack 🏗️

- **Language**: Python 3.10+
- **Framework**: Aiogram 3.x
- **Library**: yt-dlp, aiohttp
- **Database/Cache**: Redis
- **Deployment**: Railway / Docker

## Setup ⚙️

1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` file and add:
   ```env
   BOT_TOKEN=your_token
   ADMIN_ID=your_id
   REDIS_URL=your_redis_url
   ```
4. Run: `python main.py`

## Deployment 🚀

This bot is ready for deployment on **Railway**. Just connect your GitHub repo and add the environment variables.
