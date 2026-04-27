import yt_dlp
import asyncio
import os

class TikTokService:
    def __init__(self):
        self.ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/tiktok_%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }

    async def download_video(self, url):
        loop = asyncio.get_event_loop()
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
                filename = ydl.prepare_filename(info)
                return {
                    'title': info.get('title', 'TikTok Video'),
                    'file_path': filename,
                    'author': info.get('uploader', 'Unknown')
                }
        except Exception as e:
            print(f"TikTok download error: {e}")
            return None
