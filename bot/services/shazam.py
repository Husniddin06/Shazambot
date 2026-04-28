import aiohttp
import os
import logging

class ShazamService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('SHAZAM_API_KEY')
        self.url = "https://shazam-api-free.p.rapidapi.com/shazam/recognize/"
        self.host = "shazam-api-free.p.rapidapi.com"

    async def identify(self, file_path):
        if not self.api_key:
            return {"error": "Shazam API key sozlanmagan"}

        headers = {
            "x-rapidapi-key": self.api_key,
            "x-rapidapi-host": self.host
        }

        try:
            data = aiohttp.FormData()
            # RapidAPI shazam-api-free uchun faylni yuborish
            data.add_field('upload_file', open(file_path, 'rb'), filename=os.path.basename(file_path))
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, data=data, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        # Natijani qayta ishlash
                        if result and 'track' in result:
                            track = result['track']
                            return {
                                "title": track.get('title', 'Noma\'lum'),
                                "artist": track.get('subtitle', 'Noma\'lum'),
                                "image": track.get('images', {}).get('coverart')
                            }
                        return {"error": "Qo'shiq topilmadi"}
                    else:
                        return {"error": f"API xatosi: {response.status}"}
        except Exception as e:
            logging.error(f"Shazam error: {e}")
            return {"error": str(e)}
