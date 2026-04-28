import yt_dlp
import os
import logging

def download(url, mp3=False):
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
        
    output_template = "downloads/%(id)s.%(ext)s"
    
    # Telegram 50MB limit: best[filesize<50M]
    opts = {
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "format": "bestaudio[filesize<50M]/best[filesize<50M]/best" if mp3 else "bestvideo[ext=mp4][filesize<50M]+bestaudio[ext=m4a]/best[ext=mp4][filesize<50M]/best[filesize<50M]",
    }

    if mp3:
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if mp3:
                filename = filename.rsplit('.', 1)[0] + ".mp3"
            
            # Final size check
            if os.path.exists(filename) and os.path.getsize(filename) > 50 * 1024 * 1024:
                if os.path.exists(filename): os.remove(filename)
                raise Exception("Fayl 50MB dan katta. Telegram bot orqali yuborib bo'lmaydi.")
                
            return filename
    except Exception as e:
        logging.error(f"Download error: {e}")
        raise e
