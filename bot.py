import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from config import BOT_TOKEN
from db import conn, cursor
from languages import texts
from subscription import check_sub
from admin import register_admin

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

register_admin(dp)


# AUTO LANGUAGE
def get_lang(user):
    if user.language_code and user.language_code.startswith("ru"):
        return "ru"
    elif user.language_code and user.language_code.startswith("uz"):
        return "uz"
    return "en"


# START
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    user_id = msg.from_user.id

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        lang = get_lang(msg.from_user)
        cursor.execute("INSERT INTO users VALUES (?,?)", (user_id, lang))
        conn.commit()
    else:
        lang = user[1]

    # CHECK SUB
    if not await check_sub(user_id):
        await msg.answer(texts[lang]["sub"])
        return

    await msg.answer(texts[lang]["start"])


# SIMPLE MESSAGE (test uchun)
@dp.message_handler()
async def echo(msg: types.Message):
    await msg.answer("🎵 Musiqa yubor yoki link tashla")


if name == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp)

from inline_buttons import music_buttons
