from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def watched_kb(film_id: int) -> InlineKeyboardMarkup:
    """
    Reklama ko'rsatilgandan so'ng videoni tomosha qilishga taklif.
    Bu yerda bitta tugma: "Videoni ko'rish".
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Смотреть видео", callback_data=f"watch:{film_id}")]
    ])


def favorites_kb(film_id: int, is_fav: bool) -> InlineKeyboardMarkup:
    """
    Video ostidagi klaviatura — faqat sevimlilar tugmasi.
    """
    text = "⭐ Sevimlilardan o'chirish" if is_fav else "⭐ Sevimlilarga qo'shish"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=text, callback_data=f"fav:{film_id}")]
    ])
