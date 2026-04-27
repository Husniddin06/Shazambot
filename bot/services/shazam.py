from shazamio import Shazam


async def detect_song(file_path):
    shazam = Shazam()

    try:
        result = await shazam.recognize_song(file_path)

        track = result.get("track", {})
        title = track.get("title", "Unknown")
        artist = track.get("subtitle", "Unknown")

        return f"🎵 {title} - {artist}"

    except Exception as e:
        print(e)
        return "❌ Aniqlanmadi"
