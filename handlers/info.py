import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.main_menu import get_main_menu_keyboard

logger = logging.getLogger(__name__)
router = Router()


# ИНСТРУКЦИЯ
@router.callback_query(F.data == "help")
async def help_root(callback: CallbackQuery):
    text = (
        "📖 <b>Инструкция</b>\n\n"
        "• Найдите фильм по названию или через «Подборки/Фильтр».\n"
        "• Нажмите «Смотреть рекламу», затем «▶️ Смотреть» — видео придёт в чат.\n"
        "• Хотите без рекламы? Загляните в раздел «VIP бесплатно».\n\n"
        "Выберите раздел ниже:"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Как смотреть", callback_data="help_watch")],
        [InlineKeyboardButton(text="🎛 Фильтр и поиск", callback_data="help_filter")],
        [InlineKeyboardButton(text="❓ Частые вопросы", callback_data="help_faq")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")],
    ])
    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "help_watch")
async def help_watch(callback: CallbackQuery):
    text = (
        "▶️ <b>Как посмотреть фильм</b>\n\n"
        "1) Откройте карточку фильма → «📺 Смотреть рекламу».\n"
        "2) В мини-приложении дождитесь 2 экранов рекламы и нажмите «Вернуться к просмотру».\n"
        "3) Бот пришлёт сообщение «Смотреть видео 👇». Нажмите «▶️ Смотреть» — видео придёт в чат.\n\n"
        "Если реклама не загрузилась — просто откройте мини-окно ещё раз."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Назад к инструкции", callback_data="help")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")],
    ])
    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "help_filter")
async def help_filter(callback: CallbackQuery):
    text = (
        "🎛️ <b>Фильтр и поиск</b>\n\n"
        "• Введите точное название, например <code>Интерстеллар</code>.\n"
        "• «Фильтр» — выберите жанр/год/качество.\n"
        "• «Подборки» — готовые коллекции по темам.\n\n"
        "Не нашли? Попробуйте альтернативное написание (латиницей/русским)."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔎 Начать поиск", callback_data="search")],
        [InlineKeyboardButton(text="↩️ Назад к инструкции", callback_data="help")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")],
    ])
    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "help_faq")
async def help_faq(callback: CallbackQuery):
    text = (
        "❓ <b>FAQ</b>\n\n"
        "• <b>Видео не пришло</b> — проверьте интернет и повторите «Смотреть рекламу».\n"
        "• <b>Хочу без рекламы</b> — откройте «VIP бесплатно».\n"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Назад к инструкции", callback_data="help")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")],
    ])
    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()


#  VIP БЕСПЛАТНО
@router.callback_query(F.data == "vip")
async def vip_root(callback: CallbackQuery):
    text = (
        "👑 <b>VIP бесплатно</b>\n\n"
        "Что даёт VIP:\n"
        "• Просмотр без рекламы\n\n"
        "Как получить бесплатно — выберите ниже:"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💡 Как получить", callback_data="vip_how")],
        [InlineKeyboardButton(text="🎁 Пригласить друзей", callback_data="vip_invite")],
        [InlineKeyboardButton(text="ℹ️ Преимущества", callback_data="vip_benefits")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")],
    ])
    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "vip_how")
async def vip_how(callback: CallbackQuery):
    text = (
        "💡 <b>Как получить VIP бесплатно</b>\n\n"
        "1) Пригласи 10 друзей по персональной ссылке.\n"
        "2) Каждый должен запустить бота по ссылке и открыть главное меню.\n"
        "3) Когда выполнится — VIP активируется автоматически в «Настройках»."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Пригласить друзей", callback_data="vip_invite")],
        [InlineKeyboardButton(text="↩️ Назад к VIP", callback_data="vip")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")],
    ])
    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "vip_invite")
async def vip_invite(callback: CallbackQuery):
    me = await callback.bot.get_me()
    username = me.username or "YourBot"
    user_id = callback.from_user.id
    deep_link = f"https://t.me/{username}?start={user_id}"

    text = (
        "🎁 <b>Пригласить друзей</b>\n\n"
        "Отправь эту ссылку друзьям. Когда 10 человек запустят бота по ссылке, "
        "VIP активируется автоматически.\n\n"
        f"<code>{deep_link}</code>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Поделиться с друзьями", callback_data="ref_share")],  # <- НОВАЯ КНОПКА
        [InlineKeyboardButton(text="↩️ Назад к VIP", callback_data="vip")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")],
    ])
    await callback.message.answer(text, reply_markup=kb, disable_web_page_preview=True)
    await callback.answer()

@router.callback_query(F.data == "vip_benefits")
async def vip_benefits(callback: CallbackQuery):
    text = (
        "ℹ️ <b>Преимущества VIP</b>\n\n"
        "• Просмотр без рекламы\n"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Назад к VIP", callback_data="vip")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")],
    ])
    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()
