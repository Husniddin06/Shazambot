from aiogram import Router, types, F
from aiogram.filters import Command
from bot.services.youtube import YouTubeService
from bot.services.tiktok import TikTokService
from bot.services.instagram import InstagramService
from bot.utils.cache import CacheService
import os

router = Router()
yt = YouTubeService()
tt = TikTokService()
ig = InstagramService()
cache = CacheService()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Salom {message.from_user.full_name}! 👋\n\n"
        "Men media yuklovchi botman. Menga quyidagi linklarni yuborishingiz mumkin:\n"
        "• YouTube (Video/Audio)\n"
        "• TikTok (Suv belgisiz)\n"
        "• Instagram (Reels/Post)\n"
        "• VK\n\n"
        "Shuningdek, qo'shiq nomini yozsangiz, uni YouTube-dan topib beraman! 🎵"
    )

@router.message(F.text.contains("youtube.com") | F.text.contains("youtu.be"))
async def handle_youtube(message: types.Message):
    url = message.text
    
    # Cache tekshirish (faqat Redis bo'lsa ishlaydi)
    cached = await cache.get(url)
    if cached:
        try:
            await message.answer_audio(cached['file_id'], caption=f"{cached['title']} (Cached ⚡)")
            return
        except:
            pass

    msg = await message.answer("Yuklanmoqda... ⏳")
    result = await yt.download_audio(url)
    
    if result:
        audio = await message.answer_audio(
            types.FSInputFile(result['file_path']), 
            caption=result['title']
        )
        # Cachega saqlash (Redis bo'lsa)
        await cache.set(url, {'file_id': audio.audio.file_id, 'title': result['title']})
        await msg.delete()
        # Faylni o'chirish (diskda joy egallamasligi uchun)
        if os.path.exists(result['file_path']):
            os.remove(result['file_path'])
    else:
        await msg.edit_text("Xatolik yuz berdi ❌")

@router.message(F.text.contains("tiktok.com"))
async def handle_tiktok(message: types.Message):
    url = message.text
    msg = await message.answer("TikTok yuklanmoqda... ⏳")
    result = await tt.download_video(url)
    if result:
        await message.answer_video(types.FSInputFile(result['file_path']))
        await msg.delete()
        if os.path.exists(result['file_path']):
            os.remove(result['file_path'])
    else:
        await msg.edit_text("TikTok yuklashda xatolik ❌")

@router.message(F.text.contains("instagram.com"))
async def handle_instagram(message: types.Message):
    url = message.text
    msg = await message.answer("Instagram yuklanmoqda... ⏳")
    result = await ig.download_media(url)
    if result:
        await message.answer_video(types.FSInputFile(result['file_path']))
        await msg.delete()
        if os.path.exists(result['file_path']):
            os.remove(result['file_path'])
    else:
        await msg.edit_text("Instagram yuklashda xatolik ❌")

# Qo'shiq nomi bilan qidirish (YouTube orqali)
@router.message(F.text)
async def handle_search(message: types.Message):
    if message.text.startswith('/'): return
    
    query = message.text
    msg = await message.answer(f"🔍 '{query}' qidirilmoqda...")
    
    # YouTube-dan qidirish logikasi (yt-dlp search ishlatamiz)
    search_url = f"ytsearch1:{query}"
    result = await yt.download_audio(search_url)
    
    if result:
        await message.answer_audio(
            types.FSInputFile(result['file_path']), 
            caption=result['title']
        )
        await msg.delete()
        if os.path.exists(result['file_path']):
            os.remove(result['file_path'])
    else:
        await msg.edit_text("Hech narsa topilmadi 😕")
