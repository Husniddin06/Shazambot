import yt_dlp
import os

def download(url, mp3=False):
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        
    output_template = "downloads/%(id)s.%(ext)s"
    
    opts = {
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
    }

    if mp3:
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        
        if mp3:
            # yt-dlp might change extension after postprocessing
            filename = filename.rsplit('.', 1)[0] + ".mp3"
            
    return filename
