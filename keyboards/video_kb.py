from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def watched_kb(film_id: int) -> InlineKeyboardMarkup:
    """
    Сообщение-приглашение смотреть после рекламы.
    Тут ОДНА кнопка «Смотреть видео».
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Смотреть видео", callback_data=f"watch:{film_id}")]
    ])


def favorites_kb(film_id: int, is_fav: bool) -> InlineKeyboardMarkup:
    """
    Клавиатура под самим видео — ТОЛЬКО избранное.
    """
    text = "⭐ Удалить из избранного" if is_fav else "⭐ В избранное"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=f"fav:{film_id}")]
    ])
