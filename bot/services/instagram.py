import yt_dlp
import asyncio
import os

class InstagramService:
    def __init__(self):
        self.ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/insta_%(id)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
        }

    async def download_media(self, url):
        loop = asyncio.get_event_loop()
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
                filename = ydl.prepare_filename(info)
                return {
                    'title': info.get('title', 'Instagram Media'),
                    'file_path': filename,
                    'type': 'video' if info.get('ext') == 'mp4' else 'image'
                }
        except Exception as e:
            print(f"Instagram download error: {e}")
            return None
