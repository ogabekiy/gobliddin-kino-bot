import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from utils.db import get_top_tags, get_films_by_tag

logger = logging.getLogger(__name__)
router = Router()


class FilterState(StatesGroup):
    active = State()   # пользователь находится в мастере фильтра


def _kb_genres(selected: str | None) -> InlineKeyboardMarkup:
    # жанры берём из БД; если пусто — дефолты
    tags = get_top_tags(limit=12)
    if not tags:
        tags = ["Фантастика", "Боевик", "Комедия", "Драма", "Ужасы", "Семейный"]

    rows = []
    for tag in tags:
        tag_code = tag.lower()
        shown = f"✅ {tag}" if selected == tag_code else tag
        rows.append([InlineKeyboardButton(text=shown, callback_data=f"f_genre:{tag_code}")])
    rows.append([InlineKeyboardButton(text="✅ Применить", callback_data="f_apply")])
    rows.append([InlineKeyboardButton(text="🗑 Сбросить", callback_data="f_reset")])
    rows.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _kb_after_apply(titles: list[str]) -> InlineKeyboardMarkup:
    rows = []
    for t in titles:
        rows.append([InlineKeyboardButton(text=f"🎬 {t}", callback_data=f"watch:{t}")])
    rows.append([InlineKeyboardButton(text="🎛 Изменить жанр", callback_data="filter")])
    rows.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == "filter")
async def filter_root(callback: CallbackQuery, state: FSMContext):
    """Запуск мастера фильтра: оставляем только выбор жанра."""
    await state.set_state(FilterState.active)
    await state.update_data(genre=None)

    await callback.message.answer(
        "🎛 <b>Фильтр</b>\n\nВыбери <b>жанр</b> для подсказок при поиске. "
        "Можешь в любой момент изменить или сбросить.",
        reply_markup=_kb_genres(selected=None),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("f_genre:"))
async def set_genre(callback: CallbackQuery, state: FSMContext):
    """Отмечаем выбранный жанр (переключатель)."""
    code = callback.data.split(":", 1)[1].strip().lower()
    await state.update_data(genre=code)
    await callback.message.edit_reply_markup(reply_markup=_kb_genres(selected=code))
    await callback.answer("Жанр выбран")


@router.callback_query(F.data == "f_reset")
async def reset_filter(callback: CallbackQuery, state: FSMContext):
    """Сброс выбранного жанра."""
    await state.update_data(genre=None)
    await callback.message.edit_reply_markup(reply_markup=_kb_genres(selected=None))
    await callback.answer("Фильтр сброшен")


@router.callback_query(F.data == "f_apply")
async def apply_filter(callback: CallbackQuery, state: FSMContext):
    """
    Применяем фильтр:
    - если жанр выбран — показываем 8 подсказок по БД с кнопками "Смотреть";
    - если нет — просто просим выбрать.
    """
    data = await state.get_data()
    genre = (data.get("genre") or "").strip().lower()

    if not genre:
        await callback.answer("Сначала выбери жанр", show_alert=True)
        return

    films = get_films_by_tag(genre, limit=8)
    titles = [row[0] for row in films]

    if not titles:
        await callback.message.answer(
            f"По жанру «{genre}» пока ничего не нашлось. Выбери другой жанр.",
            reply_markup=_kb_genres(selected=None),
        )
        await callback.answer()
        return

    await callback.message.answer(
        f"✅ Фильтр применён.\nЖанр: <b>{genre}</b>\n\n"
        "Выбери фильм ниже или измени жанр:",
        reply_markup=_kb_after_apply(titles),
    )
    await callback.answer()
