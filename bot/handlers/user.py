from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from bot.services.youtube import YouTubeService
from bot.services.tiktok import TikTokService
from bot.services.instagram import InstagramService
from bot.services.shazam import ShazamService
from bot.utils.cache import CacheService
import os

router = Router()
yt = YouTubeService()
tt = TikTokService()
ig = InstagramService()
shazam = ShazamService()
cache = CacheService()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"Salom {message.from_user.full_name}! 👋\n\n"
        "Men media yuklovchi va musiqa aniqlovchi botman.\n\n"
        "Menga quyidagilarni yuborishingiz mumkin:\n"
        "• 🔗 **Linklar**: YouTube, TikTok, Instagram, VK\n"
        "• 🎤 **Ovozli xabar (Voice)**: Qo'shiqni aniqlash uchun\n"
        "• 🔍 **Matn**: Qo'shiqni nomi bilan qidirish uchun\n\n"
        "Hozircha link yoki ovozli xabar yuborib ko'ring!"
    )

@router.message(F.voice)
async def handle_voice(message: types.Message, bot: Bot):
    msg = await message.answer("Qo'shiq aniqlanmoqda... 🎧")
    
    # Ovozli xabarni yuklab olish
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = f"downloads/{file_id}.ogg"
    await bot.download_file(file.file_path, file_path)
    
    # Shazam orqali aniqlash
    result = await shazam.identify(file_path)
    
    if "error" not in result:
        title = result.get('title')
        artist = result.get('artist')
        caption = f"🎵 Topildi: **{title} - {artist}**\n\nYuklab beraymi?"
        
        if result.get('image'):
            await message.answer_photo(result['image'], caption=caption)
        else:
            await message.answer(caption)
        
        # Avtomatik YouTube-dan qidirib yuklab berish taklifi yoki qidiruv
        search_query = f"{artist} {title}"
        yt_res = await yt.download_audio(f"ytsearch1:{search_query}")
        if yt_res:
            await message.answer_audio(types.FSInputFile(yt_res['file_path']), caption=f"{title} - {artist}")
            if os.path.exists(yt_res['file_path']):
                os.remove(yt_res['file_path'])
        
        await msg.delete()
    else:
        await msg.edit_text(f"Afsuski, qo'shiqni aniqlab bo'lmadi: {result['error']}")
    
    # Vaqtinchalik faylni o'chirish
    if os.path.exists(file_path):
        os.remove(file_path)

@router.message(F.text.contains("youtube.com") | F.text.contains("youtu.be"))
async def handle_youtube(message: types.Message):
    url = message.text
    cached = await cache.get(url)
    if cached:
        try:
            await message.answer_audio(cached['file_id'], caption=f"{cached['title']} (Cached ⚡)")
            return
        except: pass

    msg = await message.answer("Yuklanmoqda... ⏳")
    result = await yt.download_audio(url)
    if result:
        audio = await message.answer_audio(types.FSInputFile(result['file_path']), caption=result['title'])
        await cache.set(url, {'file_id': audio.audio.file_id, 'title': result['title']})
        await msg.delete()
        if os.path.exists(result['file_path']): os.remove(result['file_path'])
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
        if os.path.exists(result['file_path']): os.remove(result['file_path'])
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
        if os.path.exists(result['file_path']): os.remove(result['file_path'])
    else:
        await msg.edit_text("Instagram yuklashda xatolik ❌")

@router.message(F.text)
async def handle_search(message: types.Message):
    if message.text.startswith('/'): return
    query = message.text
    msg = await message.answer(f"🔍 '{query}' qidirilmoqda...")
    result = await yt.download_audio(f"ytsearch1:{query}")
    if result:
        await message.answer_audio(types.FSInputFile(result['file_path']), caption=result['title'])
        await msg.delete()
        if os.path.exists(result['file_path']): os.remove(result['file_path'])
    else:
        await msg.edit_text("Hech narsa topilmadi 😕")
