import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from bot.config import BOT_TOKEN
from bot.handlers import user, admin

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)

async def main():
    # Downloads papkasini yaratish
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Routerni ulash
    dp.include_router(admin.router)
    dp.include_router(user.router)

    logging.info("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi")
