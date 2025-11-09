from __future__ import annotations

import logging
from typing import Dict, List, Tuple

from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)

# клавиатура раздела «Поиск»
from keyboards.search_menu import get_search_menu_keyboard

# БД: расширенный поиск по названию/тегам
from utils.db import search_films_by_title_or_tags

router = Router()
logger = logging.getLogger(__name__)

# Тексты, которые НЕ считаем поисковым запросом
IGNORE_TEXTS = {
    "смотреть", "▶️ смотреть",
    "смотреть рекламу", "📺 смотреть рекламу",
    "главное меню", "меню",
    "инструкция", "vip бесплатно", "vip", "настройки",
    "результаты поиска",
}

# Запоминаем последнюю выдачу и запрос пользователя
_LAST_QUERY: Dict[int, str] = {}
# [(id, title, description), ...]
_LAST_RESULTS: Dict[int, List[Tuple[int, str, str]]] = {}


def _kb_single(title: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎬 Смотреть", callback_data=f"watch:{title}")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")],
        ]
    )


def _kb_list(rows: List[Tuple[int, str, str]]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"🎬 {title}", callback_data=f"watch:{title}")]
        for (_id, title, _desc) in rows[:10]
    ]
    buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data == "search")
async def search_start(callback: CallbackQuery):
    """Открытие раздела «Поиск» — как было у тебя раньше."""
    await callback.message.answer(
        "🔍 Чтобы увидеть результаты поиска, просто напиши название фильма "
        "или нажми <b>«Результаты поиска»</b>\n\n"
        "💡 Не получилось — нажми кнопку «Инструкция»",
        reply_markup=get_search_menu_keyboard(),
    )
    await callback.answer()


@router.message(F.text & ~F.text.startswith("/"))
async def handle_text_search(message: Message):
    """Любой обычный текст — считаем запросом (кроме служебных фраз)."""
    query = (message.text or "").strip()
    if not query:
        return
    if query.lower() in IGNORE_TEXTS:
        return

    rows = search_films_by_title_or_tags(query, limit=10)  # [(id, title, desc)]
    _LAST_QUERY[message.from_user.id] = query
    _LAST_RESULTS[message.from_user.id] = rows

    if not rows:
        await message.answer("❌ Ничего не найдено по вашему запросу.")
        return

    # Если есть точное совпадение по названию ИЛИ найден ровно один — сразу карточка фильма
    exact = next((r for r in rows if r[1].lower() == query.lower()), None)
    if exact or len(rows) == 1:
        _id, title, description = exact if exact else rows[0]
        text = f"🎬 <b>{title}</b>\n{description}\n\nВыберите действие:"
        await message.answer(text, reply_markup=_kb_single(title))
        return

    # Иначе — список результатов
    await message.answer(
        f"🔎 Результаты по запросу: <b>{query}</b>",
        reply_markup=_kb_list(rows),
    )


@router.callback_query(F.data == "search_results")
async def show_last_results(callback: CallbackQuery):
    """Кнопка «Результаты поиска» из главного меню — повторяем последнюю выдачу."""
    user_id = callback.from_user.id
    rows = _LAST_RESULTS.get(user_id, [])
    query = _LAST_QUERY.get(user_id)

    if not rows:
        await callback.message.answer("🔎 Сначала отправьте название фильма сообщением.")
        await callback.answer()
        return

    if len(rows) == 1:
        _id, title, description = rows[0]
        text = f"🎬 <b>{title}</b>\n{description}\n\nВыберите действие:"
        await callback.message.answer(text, reply_markup=_kb_single(title))
    else:
        await callback.message.answer(
            f"🔎 Результаты по запросу: <b>{query}</b>",
            reply_markup=_kb_list(rows),
        )

    await callback.answer()
