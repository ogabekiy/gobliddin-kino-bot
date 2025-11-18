from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔍 Qidirishni boshlash ", switch_inline_query_current_chat=""),
            InlineKeyboardButton(text="🎁 VIP — bepul ", callback_data="vip")
        ],
        [
            InlineKeyboardButton(text="🎬 Tanlovlar", callback_data="collections"),
            InlineKeyboardButton(text="🎛 Filtr", callback_data="filter")
        ],
        [
            InlineKeyboardButton(text="📖 Qo‘llanma", callback_data="help"),
            InlineKeyboardButton(text="⚙ Sozlamalar", callback_data="settings")
        ],
        [
            InlineKeyboardButton(text="🎞 Kod orqali film olish", callback_data="get_movie_by_code")
        ],
        [
            InlineKeyboardButton(text="⭐ Sevimlilar", callback_data="favorites")
        ]
    ])
