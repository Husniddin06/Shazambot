import yt_dlp
import asyncio
import os

class YouTubeService:
    def __init__(self):
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
        }

    async def download_audio(self, url):
        loop = asyncio.get_event_loop()
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
                filename = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                return {
                    'title': info.get('title', 'Unknown Title'),
                    'file_path': filename,
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', None)
                }
        except Exception as e:
            print(f"YouTube download error: {e}")
            return None

    async def download_video(self, url):
        video_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'quiet': True,
        }
        loop = asyncio.get_event_loop()
        try:
            with yt_dlp.YoutubeDL(video_opts) as ydl:
                info = await loop.run_in_executor(None, lambda: ydl.extract_info(url, download=True))
                filename = ydl.prepare_filename(info)
                return {
                    'title': info.get('title', 'Unknown Title'),
                    'file_path': filename,
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail', None)
                }
        except Exception as e:
            print(f"YouTube video download error: {e}")
            return None
