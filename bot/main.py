import asyncio
import logging
import os
import shutil
import time
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    LabeledPrice, PreCheckoutQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN, ADMIN_ID, PREMIUM_DAYS
from bot.downloader import download, is_allowed_url, DownloadError, is_youtube_url, extract_youtube_id, get_playlist_info
from bot.rate_limit import check_limit
from bot.ai import ask_ai
from bot.music import recommend_music
from bot.i18n import t, get_lang, set_lang, has_lang
from utils.premium import is_premium, set_premium, track_user, increment_downloads, get_stats
from utils.file_cache import get_file_id, set_file_id
from utils import history, favorites, limits, quality as quality_mod, bans, queries

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logging.getLogger("aiogram").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN .env faylida ko'rsatilmagan!")

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

def main_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_help"), callback_data="show_help"),
         InlineKeyboardButton(text=t(lang, "btn_lang"), callback_data="show_lang")],
        [InlineKeyboardButton(text=t(lang, "btn_profile"), callback_data="show_profile"),
         InlineKeyboardButton(text=t(lang, "btn_quality"), callback_data="show_quality")],
        [InlineKeyboardButton(text=t(lang, "btn_history"), callback_data="show_history"),
         InlineKeyboardButton(text=t(lang, "btn_favorites"), callback_data="show_favorites"),
         InlineKeyboardButton(text=t(lang, "btn_top"), callback_data="show_top")],
        [InlineKeyboardButton(text=t(lang, "btn_premium"), callback_data="premium_menu")],
    ])

async def _guard(m: types.Message) -> str | None:
    if not m.from_user: return None
    if bans.is_banned(m.from_user.id):
        try: await m.answer(t(get_lang(m.from_user.id), "you_are_banned"))
        except: pass
        return None
    if not has_lang(m.from_user.id):
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru"),
             InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="set_lang_uz"),
             InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en")]
        ])
        await m.answer("Выберите язык / Tilni tanlang / Choose language:", reply_markup=kb)
        return None
    track_user(m.from_user.id)
    return get_lang(m.from_user.id)

@dp.message(Command("start"))
async def start(m: types.Message):
    lang = await _guard(m)
    if not lang: return
    premium_label = " 👑" if is_premium(m.from_user.id) else ""
    await m.answer(f"{t(lang, 'start_title')}{premium_label}\n\n{t(lang, 'start_body')}", reply_markup=main_keyboard(lang))

# --- Handlers for Menu Buttons ---
@dp.callback_query(F.data == "show_profile")
async def show_profile(call: types.CallbackQuery):
    lang = get_lang(call.from_user.id)
    premium = "✅" if is_premium(call.from_user.id) else "❌"
    rem = limits.remaining(call.from_user.id)
    await call.message.answer(f"👤 <b>Profil:</b>\n\nID: <code>{call.from_user.id}</code>\nPremium: {premium}\nBugungi limit: {rem}")
    await call.answer()

@dp.callback_query(F.data == "show_history")
async def show_history(call: types.CallbackQuery):
    lang = get_lang(call.from_user.id)
    hist = history.get(call.from_user.id)
    if not hist: return await call.answer("Tarix bo'sh", show_alert=True)
    text = "📜 <b>Oxirgi yuklashlar:</b>\n\n"
    for i, item in enumerate(hist[:10], 1):
        text += f"{i}. {item['title']}\n"
    await call.message.answer(text)
    await call.answer()

@dp.callback_query(F.data == "show_quality")
async def show_quality(call: types.CallbackQuery):
    lang = get_lang(call.from_user.id)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="128 kbps", callback_data="set_q_128"),
         InlineKeyboardButton(text="192 kbps", callback_data="set_q_192"),
         InlineKeyboardButton(text="320 kbps (Premium)", callback_data="set_q_320")]
    ])
    await call.message.answer("MP3 sifatini tanlang:", reply_markup=kb)
    await call.answer()

@dp.callback_query(F.data.startswith("set_q_"))
async def set_quality(call: types.CallbackQuery):
    q = call.data.split("_")[-1]
    if q == "320" and not is_premium(call.from_user.id):
        return await call.answer("320 kbps faqat Premium uchun!", show_alert=True)
    quality_mod.set_(call.from_user.id, q)
    await call.answer(f"Sifat {q} kbps ga o'zgartirildi")

# --- Progress Hook ---
class _ProgressUpdater:
    def __init__(self, bot, chat_id, msg_id, lang):
        self.bot = bot; self.chat_id = chat_id; self.msg_id = msg_id; self.lang = lang
        self.last_update = 0.0; self.last_percent = -1
        self.loop = asyncio.get_event_loop()
    def hook(self, d: dict):
        try:
            status = d.get("status")
            if status == "downloading":
                total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                done = d.get("downloaded_bytes") or 0
                if total <= 0: return
                pct = int(done * 100 / total)
                now = time.time()
                if pct == self.last_percent or now - self.last_update < 2.0: return
                self.last_percent = pct; self.last_update = now
                asyncio.run_coroutine_threadsafe(self._safe_edit(t(self.lang, "download_progress", percent=pct)), self.loop)
            elif status == "finished":
                asyncio.run_coroutine_threadsafe(self._safe_edit(t(self.lang, "download_uploading")), self.loop)
        except: pass
    async def _safe_edit(self, text: str):
        try: await self.bot.edit_message_text(chat_id=self.chat_id, message_id=self.msg_id, text=text)
        except: pass

async def _do_download(chat_id, user_id, url, want_mp3, lang, status_msg=None):
    video_id = extract_youtube_id(url) if is_youtube_url(url) else None
    if status_msg is None: status_msg = await bot.send_message(chat_id, t(lang, "downloading"))
    
    if video_id:
        cached = get_file_id(video_id, want_mp3)
        if cached:
            try:
                if want_mp3: await bot.send_audio(chat_id, cached, caption=t(lang, "from_cache"))
                else: await bot.send_video(chat_id, cached, caption=t(lang, "from_cache"))
                await status_msg.delete()
                increment_downloads(); limits.record_download(user_id)
                return
            except: pass

    work_dir = None
    try:
        q = quality_mod.get(user_id)
        progress = _ProgressUpdater(bot, chat_id, status_msg.message_id, lang)
        file, work_dir = await asyncio.to_thread(download, url, want_mp3, q, progress.hook)
        if want_mp3:
            sent = await bot.send_audio(chat_id, types.FSInputFile(file))
            file_id = sent.audio.file_id if sent.audio else None
        else:
            sent = await bot.send_video(chat_id, types.FSInputFile(file))
            file_id = sent.video.file_id if sent.video else None
        await status_msg.delete()
        if video_id and file_id: set_file_id(video_id, want_mp3, file_id)
        increment_downloads(); limits.record_download(user_id)
    except Exception as e:
        await status_msg.edit_text(f"❌ {str(e)}")
    finally:
        if work_dir and os.path.exists(work_dir): shutil.rmtree(work_dir, ignore_errors=True)

@dp.message()
async def handler(m: types.Message):
    lang = await _guard(m)
    if not lang or not m.text: return
    text = m.text.strip()

    if text.startswith(("http://", "https://")):
        if not is_allowed_url(text): return await m.answer(t(lang, "site_not_supported"))
        if not limits.can_download(m.from_user.id): return await m.answer(t(lang, "limit_reached"))
        
        if "list=" in text and is_youtube_url(text):
            msg = await m.answer("⏳")
            items = await asyncio.to_thread(get_playlist_info, text)
            if not items: return await msg.edit_text("❌ Playlist bo'sh yoki xato.")
            await msg.edit_text(f"📂 Playlist: <b>{len(items)}</b> ta video topildi.")
            for item in items[:10]:
                kb = InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="🎧 MP3", callback_data=f"dl_mp3_{item['url']}"),
                    InlineKeyboardButton(text="🎬 Video", callback_data=f"dl_vid_{item['url']}")
                ]])
                await m.answer(f"🎵 {item['title']}", reply_markup=kb)
            return

        if any(x in text for x in ["tiktok.com", "instagram.com/reels", "instagram.com/p/"]):
            await _do_download(m.chat.id, m.from_user.id, text, False, lang)
            return

        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="🎧 MP3", callback_data=f"dl_mp3_{text}"),
            InlineKeyboardButton(text="🎬 Video", callback_data=f"dl_vid_{text}")
        ]])
        await m.answer("Tanlang / Выберите / Choose:", reply_markup=kb)
        return

    if not limits.can_download(m.from_user.id): return await m.answer(t(lang, "limit_reached"))
    queries.record(text)
    msg = await m.answer("⏳")
    try:
        file, work_dir = await asyncio.to_thread(download, f"ytsearch1:{text}", True, "192")
        await m.answer_audio(types.FSInputFile(file))
        await msg.delete()
        if work_dir: shutil.rmtree(work_dir, ignore_errors=True)
        increment_downloads(); limits.record_download(m.from_user.id)
    except Exception as e: await msg.edit_text(f"❌ {str(e)}")

@dp.callback_query(F.data.startswith("dl_"))
async def dl_callback(call: types.CallbackQuery):
    lang = get_lang(call.from_user.id)
    _, kind, url = call.data.split("_", 2)
    await call.answer()
    await _do_download(call.message.chat.id, call.from_user.id, url, kind == "mp3", lang, status_msg=call.message)

@dp.callback_query(F.data.startswith("set_lang_"))
async def set_lang_callback(call: types.CallbackQuery):
    lang = call.data.split("_")[-1]
    set_lang(call.from_user.id, lang)
    await call.answer(t(lang, "lang_set"))
    await call.message.edit_text(f"{t(lang, 'start_title')}\n\n{t(lang, 'start_body')}", reply_markup=main_keyboard(lang))

@dp.callback_query(F.data == "premium_menu")
async def premium_cb(call: types.CallbackQuery):
    lang = get_lang(call.from_user.id)
    text = f"{t(lang, 'premium_title')}\n\n{t(lang, 'premium_body')}{t(lang, 'premium_price', days=PREMIUM_DAYS)}"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t(lang, "premium_pay_btn"), callback_data="pay_premium")]])
    await call.message.answer(text, reply_markup=kb)
    await call.answer()

@dp.callback_query(F.data == "pay_premium")
async def pay_premium(call: types.CallbackQuery):
    lang = get_lang(call.from_user.id)
    await bot.send_invoice(chat_id=call.from_user.id, title=t(lang, "premium_invoice_title"), description=t(lang, "premium_invoice_desc"), payload="premium_subscription", provider_token="", currency="XTR", prices=[LabeledPrice(label="Premium", amount=100)])
    await call.answer()

@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@dp.message(F.successful_payment)
async def success_payment(m: types.Message):
    set_premium(m.from_user.id, days=PREMIUM_DAYS)
    await m.answer("✅ Premium faollashtirildi!")

async def run_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(run_bot())
