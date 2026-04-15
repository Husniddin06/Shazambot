import yt_dlp

def search_music(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch5',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)

            results = []

            for entry in info['entries']:
                results.append({
                    "title": entry.get("title"),
                    "url": entry.get("webpage_url")
                })

            return results

    except Exception as e:
        print(e)
        return []
