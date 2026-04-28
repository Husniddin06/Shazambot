import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.types import LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, ADMIN_ID
from bot.downloader import download
from bot.rate_limit import check_limit
from utils.redis_cache import set_premium, is_premium

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN .env faylida topilmadi!")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(m: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌟 Premium Menu", callback_data="premium_menu")]
    ])
    welcome_text = (
        "🔥 **MAX BOT ACTIVE**\n\n"
        "Men orqali media yuklashingiz, AI bilan gaplashishingiz va musiqa topishingiz mumkin!\n\n"
        "🚀 **Imkoniyatlar:**\n"
        "• YouTube, TikTok, Instagram yuklovchi\n"
        "• /ai - GPT-4o Mini bilan suhbat\n"
        "• /music - Kayfiyatga qarab musiqa\n"
        "• /premium - Cheksiz imkoniyatlar"
    )
    await m.answer(welcome_text, reply_markup=kb, parse_mode="Markdown")

@dp.message(Command("premium"))
async def premium_cmd(m: types.Message):
    await show_premium_menu(m)

@dp.callback_query(F.data == "premium_menu")
async def premium_callback(call: types.CallbackQuery):
    await call.answer()
    await show_premium_menu(call.message)

async def show_premium_menu(message: types.Message):
    text = (
        "💎 **MAX BOT PREMIUM**\n\n"
        "Premium bilan sizda quyidagi imkoniyatlar bo'ladi:\n"
        "✅ Cheksiz yuklab olish (Rate limit yo'q)\n"
        "✅ Reklamasiz foydalanish\n"
        "✅ Yuqori tezlik\n"
        "✅ AI bilan cheksiz suhbat\n\n"
        "💰 **Narxi: 100 Stars**"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 100 Stars bilan to'lash", callback_data="pay_premium")]
    ])
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "pay_premium")
async def pay_premium(call: types.CallbackQuery):
    await call.answer()
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title="MAX BOT PREMIUM",
        description="Botning barcha imkoniyatlaridan cheksiz foydalanish uchun Premium obuna.",
        payload="premium_subscription",
        provider_token="", # Telegram Stars uchun bo'sh
        currency="XTR",
        prices=[LabeledPrice(label="Premium", amount=100)]
    )

@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@dp.message(F.successful_payment)
async def success_payment(m: types.Message):
    set_premium(m.from_user.id)
    await m.answer("✨ **TABRIKLAYMIZ!** ✨\n\nSiz endi **PREMIUM** foydalanuvchisiz! Barcha cheklovlar olib tashlandi. 🚀", parse_mode="Markdown")

@dp.message(Command("ai"))
async def ai_cmd(m: types.Message, command: CommandObject):
    from bot.ai import ask_ai
    text = command.args
    if not text:
        return await m.answer("AI ga savol bering. Masalan: `/ai Salom`", parse_mode="Markdown")
    
    msg = await m.answer("🤖 AI o'ylamoqda...")
    try:
        response = await asyncio.to_thread(ask_ai, text)
        await msg.edit_text(response)
    except Exception as e:
        logger.error(f"AI Error: {e}")
        await msg.edit_text("❌ AI bilan bog'lanishda xatolik yuz berdi.")

@dp.message(Command("music"))
async def music_cmd(m: types.Message, command: CommandObject):
    from bot.music import recommend_music
    mood = command.args
    if not mood:
        return await m.answer("Kayfiyatingizni yozing. Masalan: `/music xursand`", parse_mode="Markdown")
    
    msg = await m.answer("🎵 Musiqa qidirilmoqda...")
    try:
        response = await asyncio.to_thread(recommend_music, mood)
        await msg.edit_text(response)
    except Exception as e:
        logger.error(f"Music Error: {e}")
        await msg.edit_text("❌ Musiqa tavsiya qilishda xatolik yuz berdi.")

@dp.message()
async def handler(m: types.Message):
    if not m.text or not m.text.startswith("http"):
        return
    
    if not await check_limit(m.from_user.id):
        return await m.answer("⛔ **Spam detected!** Iltimos, bir oz kutib turing yoki /premium oling.")

    text = m.text
    msg = await m.answer("⏳ **Processing...**")
    
    file = None
    try:
        is_mp3 = "mp3" in text.lower() or "audio" in text.lower()
        file = await asyncio.to_thread(download, text, mp3=is_mp3)
        
        if is_mp3:
            await m.answer_audio(types.FSInputFile(file))
        else:
            await m.answer_video(types.FSInputFile(file))
        await msg.delete()
    except Exception as e:
        logger.error(f"Handler Error: {e}")
        await msg.edit_text(f"❌ Xatolik: {str(e)}")
    finally:
        if file and os.path.exists(file):
            try:
                os.remove(file)
            except Exception as e:
                logger.error(f"File removal error: {e}")

async def run_bot():
    logger.info("Bot ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
