from aiogram import Router, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, WebAppInfo
from urllib.parse import quote
import logging

from utils.db import get_film_by_title, try_consume_free_view, is_user_vip
from utils.send_video import send_video_to_user
from keyboards.main_menu import get_main_menu_keyboard
from utils.favorites import add_favorite, remove_favorite, is_favorite  # title-based helpers

logger = logging.getLogger(__name__)
router = Router()

WEBAPP_URL = "https://web-app-ad-kappa.vercel.app"


async def build_watch_keyboard(user_id: int, title: str) -> InlineKeyboardMarkup:
    """Клавиатура под карточкой (не видео)"""
    fav = await is_favorite(user_id, title)  # title -> bool
    fav_text = "★ Sevimlilardan o'chirish" if fav else "⭐ Sevimlilarga qo'shish"
    fav_cb = f"fav:del:{title}" if fav else f"fav:add:{title}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Смотреть", callback_data=f"play:{title}")],
        [InlineKeyboardButton(text=fav_text, callback_data=fav_cb)],
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_menu")],
    ])


@router.callback_query(F.data.startswith("watch:"))
async def handle_watch(callback: CallbackQuery):
    """Показываем карточку фильма с кнопками."""
    user_id = callback.from_user.id
    title = callback.data.split("watch:", 1)[1]
    film = get_film_by_title(title)
    if not film:
        await callback.message.answer("❌ Film topilmadi.")
        await callback.answer()
        return

    title, description, _ = film
    caption = f"🎬 <b>{title}</b>\n{description}\n\n"
    if (await is_user_vip(user_id)) or try_consume_free_view(user_id):
        caption += "✅ Siz reklamasiz videoni ko'rishingiz mumkin."
        kb = await build_watch_keyboard(user_id, title)
    else:
        caption += "⚠️ Reklamani ko'rish tugmasini bosing, videoni bepul ochish uchun."
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📺 Reklamani ko'rish",
                web_app=WebAppInfo(url=f"{WEBAPP_URL}?title={quote(title)}")
            )],
            [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_menu")],
        ])

    await callback.message.answer(caption, reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith("play:"))
async def handle_play(callback: CallbackQuery):
    """Отправляем САМО видео (кнопки под видео формирует send_video_to_user)."""
    user_id = callback.from_user.id
    title = callback.data.split("play:", 1)[1]
    try:
        await send_video_to_user(callback.bot, user_id, title)
        await callback.bot.send_message(user_id, "Tayyor! Keyingi nima? 👇", reply_markup=get_main_menu_keyboard())
    except Exception as e:
        logger.exception(f"Ошибка при отправке фильма '{title}': {e}")
        await callback.bot.send_message(user_id, "🚫 Filmni yuborib bo'lmadi.")
    finally:
        await callback.answer()


# ВАЖНО: этот обработчик теперь ловит ТОЛЬКО 'fav:add:' и 'fav:del:' (карточка).
# Клики 'fav:<film_id>' из кнопки под ВИДЕО обрабатывает handlers/favorites.py.
@router.callback_query(F.data.startswith(("fav:add:", "fav:del:")))
async def handle_favorite_toggle_title(callback: CallbackQuery):
    user_id = callback.from_user.id
    try:
        prefix, action, title = callback.data.split(":", 2)
    except ValueError:
        await callback.answer("Noto'g'ri ma'lumotlar.", show_alert=True)
        return

    if action == "add":
        ok = await add_favorite(user_id, title)   # добавление по title
        await callback.answer("Sevimlilarga qo'shildi ⭐" if ok else "Qo'shib bo'lmadi", show_alert=not ok)
    elif action == "del":
        ok = await remove_favorite(user_id, title)  # удаление по title
        await callback.answer("Sevimlilardan o'chirildi" if ok else "O'chirib bo'lmadi", show_alert=not ok)
    else:
        await callback.answer("Noma'lum amal.", show_alert=True)
        return

    # обновим клавиатуру у этой же карточки
    try:
        new_kb = await build_watch_keyboard(user_id, title)
        if callback.message:
            await callback.message.edit_reply_markup(reply_markup=new_kb)
        elif callback.inline_message_id:
            await callback.bot.edit_message_reply_markup(
                inline_message_id=callback.inline_message_id,
                reply_markup=new_kb
            )
    except Exception as e:
        logger.exception(f"Не удалось обновить клавиатуру избранного: {e}")
