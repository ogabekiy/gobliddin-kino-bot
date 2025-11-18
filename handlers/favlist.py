from __future__ import annotations

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from utils.db import get_favorites, remove_favorite

PAGE_SIZE = 10
router = Router()


def _kb_favlist(rows, offset, total) -> InlineKeyboardMarkup:
    """
    rows: [(film_id, title, description)]
    Показываем в каждой строке:
      ▶️ Смотреть  -> watch:{title}  (чтобы сработал VIP/реклама флоу внутри handlers/watch.py)
      🗑 Удалить   -> favremove:{film_id}:{offset}
    """
    kb = []
    for film_id, title, _ in rows:
        kb.append([
            InlineKeyboardButton(text=f"▶️ {title}", callback_data=f"watch:{title}"),
            InlineKeyboardButton(text=" <- 🗑 Sevimlilardan o'chirish", callback_data=f"favremove:{film_id}:{offset}"),
        ])

    nav = []
    if offset > 0:
        prev_off = max(0, offset - PAGE_SIZE)
        nav.append(InlineKeyboardButton(text="◀️ Orqaga", callback_data=f"favpage:{prev_off}"))
    if offset + PAGE_SIZE < total:
        next_off = offset + PAGE_SIZE
        nav.append(InlineKeyboardButton(text="Oldinga ▶️", callback_data=f"favpage:{next_off}"))
    if nav:
        kb.append(nav)

    kb.append([InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=kb)


@router.callback_query(F.data == "favorites")
async def open_favorites(callback: CallbackQuery):
    """Открыть список избранного из меню поиска."""
    user_id = callback.from_user.id
    favs = get_favorites(user_id)  # [(film_id, title, description)]

    if not favs:
        await callback.message.answer(
            "⭐ Sevimlilar hali bo'sh.\nVideoning ostidagi «⭐ Sevimlilarga qo'shish» tugmasi bilan filmlarni qo'shing."
        )
        await callback.answer()
        return

    total = len(favs)
    await callback.message.answer(
        f"⭐ Sevimlilaringiz — {total} ta.",
        reply_markup=_kb_favlist(favs[:PAGE_SIZE], 0, total),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("favpage:"))
async def paginate_favorites(callback: CallbackQuery):
    """Пагинация списка избранного."""
    user_id = callback.from_user.id
    try:
        offset = int(callback.data.split(":", 1)[1])
    except Exception:
        await callback.answer("Noto'g'ri ma'lumotlar.", show_alert=True)
        return

    favs = get_favorites(user_id)
    total = len(favs)
    slice_rows = favs[offset: offset + PAGE_SIZE]

    try:
        await callback.message.edit_reply_markup(
            reply_markup=_kb_favlist(slice_rows, offset, total)
        )
    except Exception:
        await callback.message.answer(
            f"⭐ Sevimlilaringiz — {total} ta.",
            reply_markup=_kb_favlist(slice_rows, offset, total),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("favremove:"))
async def remove_from_favorites(callback: CallbackQuery):
    """Удалить фильм из избранного прямо из списка."""
    user_id = callback.from_user.id
    try:
        _, film_id_str, offset_str = callback.data.split(":")
        film_id = int(film_id_str)
        offset = int(offset_str)
    except Exception:
        await callback.answer("Noto'g'ri ma'lumotlar.", show_alert=True)
        return

    remove_favorite(user_id, film_id)
    favs = get_favorites(user_id)
    total = len(favs)

    if offset >= total and offset > 0:
        offset = max(0, offset - PAGE_SIZE)

    slice_rows = favs[offset: offset + PAGE_SIZE]

    try:
        await callback.message.edit_reply_markup(
            reply_markup=_kb_favlist(slice_rows, offset, total)
        )
    except Exception:
        await callback.message.answer(
            f"⭐ Sevimlilaringiz — {total} ta.",
            reply_markup=_kb_favlist(slice_rows, offset, total)
        )
    await callback.answer("Sevimlilardan o'chirildi.")
