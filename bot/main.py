import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, ADMIN_ID
from bot.downloader import download
from bot.rate_limit import check_limit

# Logging
logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(m: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌟 Premium Menu", callback_data="premium_menu")]
    ])
    await m.answer("🔥 **MAX BOT ACTIVE**\n\nMen orqali media yuklashingiz, AI bilan gaplashishingiz va musiqa topishingiz mumkin!", 
                   reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "premium_menu")
@dp.message(Command("premium"))
async def premium_menu(event):
    message = event.message if isinstance(event, types.CallbackQuery) else event
    text = (
        "💎 **MAX BOT PREMIUM**\n\n"
        "Premium bilan sizda quyidagi imkoniyatlar bo'ladi:\n"
        "✅ Cheksiz yuklab olish\n"
        "✅ Reklamasiz foydalanish\n"
        "✅ Yuqori tezlik\n"
        "✅ AI bilan cheksiz suhbat\n\n"
        "💰 **Narxi: 150 Stars**"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 150 Stars bilan to'lash", callback_data="pay_premium")]
    ])
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "pay_premium")
async def pay_premium(call: types.CallbackQuery):
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title="MAX BOT PREMIUM",
        description="Botning barcha imkoniyatlaridan cheksiz foydalanish uchun Premium obuna.",
        payload="premium_subscription",
        provider_token="", # Telegram Stars uchun bo'sh qoldiriladi
        currency="XTR",
        prices=[LabeledPrice(label="Premium", amount=150)]
    )

@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@dp.message(F.successful_payment)
async def success_payment(m: types.Message):
    await m.answer("✨ **TABRIKLAYMIZ!** ✨\n\nSiz endi **PREMIUM** foydalanuvchisiz! Barcha cheklovlar olib tashlandi. 🚀", parse_mode="Markdown")

@dp.message(Command("ai"))
async def ai_cmd(m: types.Message):
    from bot.ai import ask_ai
    text = m.text.replace("/ai", "").strip()
    if not text:
        return await m.answer("AI ga savol bering. Masalan: `/ai Salom`")
    msg = await m.answer("🤖 AI o'ylamoqda...")
    response = ask_ai(text)
    await msg.edit_text(response)

@dp.message(Command("music"))
async def music_cmd(m: types.Message):
    from bot.music import recommend_music
    mood = m.text.replace("/music", "").strip()
    if not mood:
        return await m.answer("Kayfiyatingizni yozing. Masalan: `/music xursand`")
    msg = await m.answer("🎵 Musiqa qidirilmoqda...")
    response = recommend_music(mood)
    await msg.edit_text(response)

@dp.message()
async def handler(m: types.Message):
    if not m.text: return
    
    if not check_limit(m.from_user.id):
        return await m.answer("⛔ **Spam detected!** Iltimos, bir oz kutib turing.")

    text = m.text
    if not text.startswith("http"):
        return

    msg = await m.answer("⏳ **Processing...**")
    try:
        if "mp3" in text.lower() or "audio" in text.lower():
            file = download(text, mp3=True)
            await m.answer_audio(types.FSInputFile(file))
        else:
            file = download(text)
            await m.answer_video(types.FSInputFile(file))
        await msg.delete()
        if os.path.exists(file): os.remove(file)
    except Exception as e:
        await msg.edit_text(f"❌ Xatolik: {str(e)}")

async def run_bot():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(run_bot())
