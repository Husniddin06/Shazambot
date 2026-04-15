import yt_dlp


def download(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'media.%(ext)s',
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return "media.mp3"

    except Exception as e:
        print(e)
        return None
