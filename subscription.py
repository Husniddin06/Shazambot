from aiogram import Bot
from config import BOT_TOKEN
from db import get_setting

bot = Bot(token=BOT_TOKEN)


async def check_sub(user_id):
    # majburiy obuna yoqilganmi
    force = get_setting("force_sub")

    if force != "on":
        return True

    # kanal borligini tekshirish
    channel = get_setting("channel")

    if not channel:
        return True

    try:
        member = await bot.get_chat_member(channel, user_id)

        if member.status in ["left", "kicked"]:
            return False

        return True

    except:
        return True
