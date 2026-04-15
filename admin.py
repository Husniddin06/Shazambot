from aiogram import types
from config import ADMIN_ID
from db import set_setting, get_setting, cursor


def register_admin(dp):

    # ADMIN PANEL
    @dp.message_handler(commands=["admin"])
    async def admin_panel(msg: types.Message):
        if msg.from_user.id != ADMIN_ID:
            return

        users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        channel = get_setting("channel")
        force = get_setting("force_sub")

        text = f"""
👑 ADMIN PANEL

👤 Users: {users}

📢 Channel: {channel}
🔒 Force Sub: {force}
"""

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("📢 Kanal ulash", "❌ Kanal o‘chirish")
        kb.add("🔒 Sub ON", "🔓 Sub OFF")

        await msg.answer(text, reply_markup=kb)


    # KANAL ULASH
    @dp.message_handler(lambda m: m.text == "📢 Kanal ulash")
    async def ask_channel(msg: types.Message):
        if msg.from_user.id != ADMIN_ID:
            return

        await msg.answer("Kanal username yubor: @kanal")


    @dp.message_handler(lambda m: m.text.startswith("@"))
    async def save_channel(msg: types.Message):
        if msg.from_user.id != ADMIN_ID:
            return

        set_setting("channel", msg.text)
        await msg.answer("✅ Kanal saqlandi")


    # KANAL O‘CHIRISH
    @dp.message_handler(lambda m: m.text == "❌ Kanal o‘chirish")
    async def remove_channel(msg: types.Message):
        if msg.from_user.id != ADMIN_ID:
            return

        set_setting("channel", "")
        await msg.answer("❌ Kanal olib tashlandi")


    # SUB ON
    @dp.message_handler(lambda m: m.text == "🔒 Sub ON")
    async def sub_on(msg: types.Message):
        if msg.from_user.id != ADMIN_ID:
            return

        set_setting("force_sub", "on")
        await msg.answer("✅ Majburiy obuna YOQILDI")


    # SUB OFF
    @dp.message_handler(lambda m: m.text == "🔓 Sub OFF")
    async def sub_off(msg: types.Message):
        if msg.from_user.id != ADMIN_ID:
            return

        set_setting("force_sub", "off")
        await msg.answer("❌ Majburiy obuna O‘CHIRILDI")
