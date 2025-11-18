from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_search_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📖 Qo'llanma", callback_data="help"),
            InlineKeyboardButton(text="🎁 VIP bepul", callback_data="vip")
        ],
        [
            InlineKeyboardButton(text="🎛 Filtr", callback_data="filter"),
            InlineKeyboardButton(text="🎬 To'plamlar", callback_data="collections")
        ],
        [
            InlineKeyboardButton(text="⭐ Sevimlilar", callback_data="favorites"),
            InlineKeyboardButton(text="⚙ Sozlamalar", callback_data="settings")
        ],
        [
            InlineKeyboardButton(text="🔍 Qidiruv natijalari", callback_data="search_results")
        ]
    ])
