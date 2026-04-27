import yt_dlp
import asyncio

class VKService:
    def __init__(self):
        self.ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/vk_%(id)s.%(ext)s',
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
                    'title': info.get('title', 'VK Media'),
                    'file_path': filename
                }
        except Exception as e:
            print(f"VK download error: {e}")
            return None
