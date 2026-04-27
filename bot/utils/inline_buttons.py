from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def music_buttons(url):
    kb = InlineKeyboardMarkup(row_width=2)

    kb.add(
        InlineKeyboardButton("🎧 Yuklab olish", callback_data=f"dl|{url}"),
        InlineKeyboardButton("🔗 Ochish", url=url)
    )

    return kb
