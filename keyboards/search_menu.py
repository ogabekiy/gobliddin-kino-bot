from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_search_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📖 Инструкция", callback_data="help"),
            InlineKeyboardButton(text="🎁 VIP бесплатно", callback_data="vip")
        ],
        [
            InlineKeyboardButton(text="🎛 Фильтр", callback_data="filter"),
            InlineKeyboardButton(text="🎬 Подборки", callback_data="collections")
        ],
        [
            InlineKeyboardButton(text="⭐ Избранное", callback_data="favorites"),
            InlineKeyboardButton(text="⚙ Настройки", callback_data="settings")
        ],
        [
            InlineKeyboardButton(text="🔍 Результаты поиска", callback_data="search_results")
        ]
    ])
