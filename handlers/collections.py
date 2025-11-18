import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from utils.db import get_top_tags, get_films_by_tag, get_random_films

logger = logging.getLogger(__name__)
router = Router()


def _kb_tags(tags: list[str]) -> InlineKeyboardMarkup:
    rows = []
    # bitta tugma — bitta janr
    for tag in tags:
        rows.append([InlineKeyboardButton(text=tag, callback_data=f"col_gen:{tag.lower()}")])
    # maxsus tugmalar
    rows.append([InlineKeyboardButton(text="🔥 Tasodifiy tavsiyalar", callback_data="col_random")])
    rows.append([InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _kb_titles(titles: list[str]) -> InlineKeyboardMarkup:
    rows = []
    for t in titles:
        rows.append([InlineKeyboardButton(text=f"🎬 {t}", callback_data=f"watch:{t}")])
    rows.append([InlineKeyboardButton(text="⬅️ Janrlarga", callback_data="collections")])
    rows.append([InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == "collections")
async def collections_root(callback: CallbackQuery):
    """Bo'lim — Tanlovlar: DBdan mashhur janrlarni ko'rsatadi."""
    tags = get_top_tags(limit=12)  # DBdagi chastotaga ko'ra
    if not tags:
        # Zaxira variant — agar DB bo'sh bo'lsa
        tags = ["🛸 Fantastika", "💥 Jangari", "🤣 Komediya", "😍 Drama", "👻 Ujas","🌌 Koinot"]

    kb = _kb_tags(tags)
    await callback.message.answer(
        "🎬 <b>Janrlar bo‘yicha tanlovlar</b>\n\nBizning bazadan tavsiyalarni ko‘rish uchun janrni tanlang.",
        reply_markup=kb,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("col_gen:"))
async def list_by_genre(callback: CallbackQuery):
    """Tanlangan janr bo'yicha filmlar ro'yxati (tags ustunida qidiramiz)."""
    raw = callback.data.split(":", 1)[1]
    tag = raw.strip().lower()

    films = get_films_by_tag(tag, limit=10)
    titles = [row[0] for row in films]

    if not titles:
        await callback.message.answer(
            f"😕 Hozircha «{tag}» janrida hech narsa topilmadi. Boshqa janrni sinab ko'ring.",
            reply_markup=_kb_tags(get_top_tags(limit=12)),
        )
        await callback.answer()
        return

    await callback.message.answer(
        f"📚 Tanlov — janr: <b>{tag}</b>\nQuyidan filmni tanlang:",
        reply_markup=_kb_titles(titles),
    )
    await callback.answer()


@router.callback_query(F.data == "col_random")
async def random_suggestions(callback: CallbackQuery):
    """Faqatgina DBdan bir nechta tasodifiy tavsiyalar."""
    items = get_random_films(limit=8)
    titles = [t for (t, _desc) in items]
    if not titles:
        await callback.message.answer("Hozircha baza bo'sh 😅")
        await callback.answer()
        return

    await callback.message.answer(
        "🎲 Tasodifiy tavsiyalar:",
        reply_markup=_kb_titles(titles),
    )
    await callback.answer()
