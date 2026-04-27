from aiogram import Router, types, F
from aiogram.filters import Command
import os

router = Router()
ADMIN_ID = int(os.getenv('ADMIN_ID', 0))

@router.message(Command("admin"), F.from_user.id == ADMIN_ID)
async def admin_panel(message: types.Message):
    # Bu yerda statistika va boshqa admin funksiyalari bo'ladi
    await message.answer("👑 ADMIN PANEL\n\nTez orada statistika qo'shiladi.")

@router.message(Command("broadcast"), F.from_user.id == ADMIN_ID)
async def broadcast_start(message: types.Message):
    await message.answer("Xabarni yuboring...")
