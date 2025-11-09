from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔍 Начать поиск", switch_inline_query_current_chat=""),
            InlineKeyboardButton(text="🎁 VIP бесплатно", callback_data="vip")
        ],
        [
            InlineKeyboardButton(text="🎬 Подборки", callback_data="collections"),
            InlineKeyboardButton(text="🎛 Фильтр", callback_data="filter")
        ],
        [
            InlineKeyboardButton(text="📖 Инструкция", callback_data="help"),
            InlineKeyboardButton(text="⚙ Настройки", callback_data="settings")
        ],
        [
            InlineKeyboardButton(text="🎞 Получить фильм по коду", callback_data="get_movie_by_code")
        ],
        [
            InlineKeyboardButton(text="⭐ Избранное", callback_data="favorites")
        ]
    ])
