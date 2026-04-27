from aiogram import Router, types, F
from aiogram.filters import Command
from bot.services.youtube import YouTubeService
from bot.services.tiktok import TikTokService
from bot.services.instagram import InstagramService
from bot.utils.cache import CacheService
import re

router = Router()
yt = YouTubeService()
tt = TikTokService()
ig = InstagramService()
cache = CacheService()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"Salom {message.from_user.full_name}! Men All-in-one media botman. Menga link yuboring!")

@router.message(F.text.contains("youtube.com") | F.text.contains("youtu.be"))
async def handle_youtube(message: types.Message):
    url = message.text
    # Cache tekshirish
    cached = await cache.get(url)
    if cached:
        await message.answer_audio(cached['file_id'], caption="Cached ⚡")
        return

    msg = await message.answer("Yuklanmoqda... ⏳")
    result = await yt.download_audio(url)
    if result:
        audio = await message.answer_audio(types.FSInputFile(result['file_path']), caption=result['title'])
        # Cachega saqlash (file_id bilan)
        await cache.set(url, {'file_id': audio.audio.file_id, 'title': result['title']})
        await msg.delete()
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
    else:
        await msg.edit_text("Instagram yuklashda xatolik ❌")
