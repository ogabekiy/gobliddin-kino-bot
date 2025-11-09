import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from utils.db import get_top_tags, get_films_by_tag, get_random_films

logger = logging.getLogger(__name__)
router = Router()


def _kb_tags(tags: list[str]) -> InlineKeyboardMarkup:
    rows = []
    # одна кнопка — один жанр
    for tag in tags:
        rows.append([InlineKeyboardButton(text=tag, callback_data=f"col_gen:{tag.lower()}")])
    # спец-кнопки
    rows.append([InlineKeyboardButton(text="🔥 Случайные подсказки", callback_data="col_random")])
    rows.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _kb_titles(titles: list[str]) -> InlineKeyboardMarkup:
    rows = []
    for t in titles:
        rows.append([InlineKeyboardButton(text=f"🎬 {t}", callback_data=f"watch:{t}")])
    rows.append([InlineKeyboardButton(text="⬅️ К жанрам", callback_data="collections")])
    rows.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == "collections")
async def collections_root(callback: CallbackQuery):
    """Корень раздела «Подборки»: показываем популярные жанры из БД."""
    tags = get_top_tags(limit=12)  # по частоте в БД
    if not tags:
        # запасной вариант, если в БД пусто
        tags = ["Фантастика", "Боевик", "Комедия", "Драма", "Ужасы", "Семейный"]

    kb = _kb_tags(tags)
    await callback.message.answer(
        "🎬 <b>Подборки по жанрам</b>\n\nВыбери жанр, чтобы увидеть подсказки из нашей базы.",
        reply_markup=kb,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("col_gen:"))
async def list_by_genre(callback: CallbackQuery):
    """Список фильмов по выбранному жанру (ищем в колонке tags)."""
    raw = callback.data.split(":", 1)[1]
    tag = raw.strip().lower()

    films = get_films_by_tag(tag, limit=10)
    titles = [row[0] for row in films]

    if not titles:
        await callback.message.answer(
            f"😕 Пока ничего не нашёл по жанру «{tag}». Попробуй другой жанр.",
            reply_markup=_kb_tags(get_top_tags(limit=12)),
        )
        await callback.answer()
        return

    await callback.message.answer(
        f"📚 Подборка — жанр: <b>{tag}</b>\nВыбери фильм ниже:",
        reply_markup=_kb_titles(titles),
    )
    await callback.answer()


@router.callback_query(F.data == "col_random")
async def random_suggestions(callback: CallbackQuery):
    """Просто несколько случайных подсказок из БД."""
    items = get_random_films(limit=8)
    titles = [t for (t, _desc) in items]
    if not titles:
        await callback.message.answer("Пока база пуста 😅")
        await callback.answer()
        return

    await callback.message.answer(
        "🎲 Случайные подсказки:",
        reply_markup=_kb_titles(titles),
    )
    await callback.answer()
