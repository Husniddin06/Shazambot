import asyncio
import logging
import os
import shutil
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    LabeledPrice, PreCheckoutQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN, ADMIN_ID, PREMIUM_DAYS
from bot.downloader import download, is_allowed_url, DownloadError
from bot.rate_limit import check_limit
from bot.ai import ask_ai
from bot.music import recommend_music
from utils.premium import is_premium, set_premium, track_user, increment_downloads, get_stats

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

def split_message(text: str, limit: int = 4000) -> list[str]:
    return [text[i:i + limit] for i in range(0, len(text), limit)] or [""]

@dp.message(Command("start"))
async def start(m: types.Message):
    if m.from_user:
        track_user(m.from_user.id)
    
    premium_label = " 👑" if (m.from_user and is_premium(m.from_user.id)) else ""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌟 Premium Menu", callback_data="premium_menu")],
        [InlineKeyboardButton(text="📖 Yordam", callback_data="show_help")],
    ])
    await m.answer(
        f"🔥 <b>MAX BOT ACTIVE</b>{premium_label}\n\n"
        "Men orqali media yuklashingiz, AI bilan gaplashishingiz "
        "va musiqa topishingiz mumkin!",
        reply_markup=kb,
    )

@dp.message(Command("help"))
async def help_cmd(m: types.Message):
    await _send_help(m)

@dp.callback_query(F.data == "show_help")
async def help_cb(call: types.CallbackQuery):
    await call.answer()
    if call.message:
        await _send_help(call.message)

async def _send_help(m: types.Message):
    await m.answer(
        "📖 <b>Komandalar</b>\n\n"
        "/start — botni ishga tushirish\n"
        "/ai &lt;savol&gt; — AI bilan suhbat\n"
        "/music &lt;kayfiyat&gt; — musiqa tavsiya\n"
        "/premium — Premium obuna\n"
        "/help — yordam\n\n"
        "🔗 YouTube / Instagram / TikTok / Twitter / Facebook / SoundCloud "
        "havolasini yuboring — yuklab beraman.\n\n"
        "🎵 Audio (mp3) olish uchun havoladan oldin <code>mp3</code> deb yozing.\n"
        "Masalan: <code>mp3 https://youtu.be/...</code>"
    )

@dp.message(Command("premium"))
async def premium_cmd(m: types.Message):
    await _show_premium(m)

@dp.callback_query(F.data == "premium_menu")
async def premium_cb(call: types.CallbackQuery):
    await call.answer()
    if call.message:
        await _show_premium(call.message)

async def _show_premium(message: types.Message):
    text = (
        "💎 <b>MAX BOT PREMIUM</b>\n\n"
        "Premium bilan sizda quyidagi imkoniyatlar bo'ladi:\n"
        "✅ Cheksiz yuklab olish\n"
        "✅ Reklamasiz foydalanish\n"
        "✅ Yuqori tezlik\n"
        "✅ AI bilan cheksiz suhbat\n\n"
        f"💰 <b>Narxi: 100 Stars / {PREMIUM_DAYS} kun</b>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 100 Stars bilan to'lash", callback_data="pay_premium")]
    ])
    await message.answer(text, reply_markup=kb)

@dp.callback_query(F.data == "pay_premium")
async def pay_premium(call: types.CallbackQuery):
    await call.answer()
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title="MAX BOT PREMIUM",
        description="Botning barcha imkoniyatlaridan cheksiz foydalanish uchun Premium obuna.",
        payload="premium_subscription",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Premium", amount=100)],
    )

@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@dp.message(F.successful_payment)
async def success_payment(m: types.Message):
    if m.from_user:
        set_premium(m.from_user.id, days=PREMIUM_DAYS)
    await m.answer(
        "✨ <b>TABRIKLAYMIZ!</b> ✨\n\n"
        f"Siz endi <b>PREMIUM</b> foydalanuvchisiz ({PREMIUM_DAYS} kun)! "
        "Barcha cheklovlar olib tashlandi. 🚀"
    )

@dp.message(Command("ai"))
async def ai_cmd(m: types.Message, command: CommandObject):
    if not m.from_user: return
    track_user(m.from_user.id)
    text = (command.args or "").strip()
    if not text:
        return await m.answer("AI ga savol bering. Masalan: <code>/ai Salom</code>")
    
    if not await check_limit(m.from_user.id):
        return await m.answer("⛔ Juda tez-tez so'rov! Bir oz kuting yoki /premium oling.")
    
    msg = await m.answer("🤖 AI o'ylamoqda...")
    response = await asyncio.to_thread(ask_ai, text)
    chunks = split_message(response)
    await msg.edit_text(chunks[0])
    for extra in chunks[1:]:
        await m.answer(extra)

@dp.message(Command("music"))
async def music_cmd(m: types.Message, command: CommandObject):
    if not m.from_user: return
    track_user(m.from_user.id)
    mood = (command.args or "").strip()
    if not mood:
        return await m.answer("Kayfiyatingizni yozing. Masalan: <code>/music xursand</code>")
    
    if not await check_limit(m.from_user.id):
        return await m.answer("⛔ Juda tez-tez so'rov! Bir oz kuting yoki /premium oling.")
    
    msg = await m.answer("🎵 Musiqa qidirilmoqda...")
    response = await asyncio.to_thread(recommend_music, mood)
    await msg.edit_text(response)

@dp.message(Command("stats"))
async def stats_cmd(m: types.Message):
    if not m.from_user or m.from_user.id != ADMIN_ID:
        return
    s = get_stats()
    await m.answer(
        "📊 <b>Statistika</b>\n\n"
        f"👤 Foydalanuvchilar: <b>{s['users']}</b>\n"
        f"👑 Premium: <b>{s['premium']}</b>\n"
        f"⬇️ Yuklab olishlar: <b>{s['downloads']}</b>"
    )

@dp.message(Command("broadcast"))
async def broadcast_cmd(m: types.Message, command: CommandObject):
    if not m.from_user or m.from_user.id != ADMIN_ID:
        return
    text = (command.args or "").strip()
    if not text:
        return await m.answer("Foydalanish: <code>/broadcast &lt;matn&gt;</code>")
    
    from utils.redis_cache import r
    if not r:
        return await m.answer("Redis ulanmagan, broadcast ishlamaydi.")
    
    sent, failed = 0, 0
    for uid in r.smembers("users:all"):
        try:
            await bot.send_message(int(uid), text)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)
    await m.answer(f"✅ Yuborildi: {sent}\n❌ Xato: {failed}")

@dp.message(Command("grant"))
async def grant_cmd(m: types.Message, command: CommandObject):
    if not m.from_user or m.from_user.id != ADMIN_ID:
        return
    args = (command.args or "").split()
    if not args:
        return await m.answer("Foydalanish: <code>/grant &lt;user_id&gt; [days]</code>")
    try:
        target = int(args[0])
        days = int(args[1]) if len(args) > 1 else PREMIUM_DAYS
    except ValueError:
        return await m.answer("Noto'g'ri argument.")
    
    set_premium(target, days=days)
    await m.answer(f"✅ {target} ga {days} kun premium berildi.")

@dp.message()
async def url_handler(m: types.Message):
    if not m.text or not m.from_user:
        return
    track_user(m.from_user.id)
    text = m.text.strip()
    
    want_mp3 = False
    if text.lower().startswith("mp3 "):
        want_mp3 = True
        text = text[4:].strip()
    
    if not text.startswith(("http://", "https://")):
        return
    
    if not is_allowed_url(text):
        return await m.answer(
            "❌ Bu sayt qo'llab-quvvatlanmaydi.\n"
            "Qo'llab-quvvatlanadigan: YouTube, Instagram, TikTok, Twitter/X, "
            "Facebook, SoundCloud."
        )
    
    if not await check_limit(m.from_user.id):
        return await m.answer("⛔ Juda tez-tez so'rov! Bir oz kuting yoki /premium oling.")
    
    msg = await m.answer("⏳ <b>Yuklanmoqda...</b>")
    work_dir = None
    try:
        file, work_dir = await asyncio.to_thread(download, text, want_mp3)
        if want_mp3:
            await m.answer_audio(types.FSInputFile(file))
        else:
            await m.answer_video(types.FSInputFile(file))
        await msg.delete()
        increment_downloads()
    except DownloadError as e:
        await msg.edit_text(f"❌ {e}")
    except Exception as e:
        logger.exception("url_handler xatosi")
        await msg.edit_text("❌ Kutilmagan xatolik yuz berdi.")
    finally:
        if work_dir and os.path.exists(work_dir):
            shutil.rmtree(work_dir, ignore_errors=True)

async def run_bot():
    logger.info("Bot ishga tushdi.")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(run_bot())
