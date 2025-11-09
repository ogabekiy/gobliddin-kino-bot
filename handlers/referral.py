from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from urllib.parse import quote

router = Router()


@router.callback_query(F.data == "ref_share")
async def referral_share(callback: CallbackQuery, bot: Bot):
    """
    Отправляет красивый пост с реферальной ссылкой и кнопками для шаринга.
    """
    user_id = callback.from_user.id
    me = await bot.get_me()
    bot_username = me.username or "YourBot"
    ref_link = f"https://t.me/{bot_username}?start={user_id}"

    # Текст поста
    post_text = (
        "👋 Привет!\n\n"
        "🎬 Я нашел крутого бота для просмотра фильмов и сериалов!\n\n"
        "✨ Что внутри:\n"
        "🎥 Огромная коллекция фильмов\n"
        "📺 Сериалы всех жанров\n"
        "🆓 Бесплатный просмотр\n"
        "⚡️ Быстрая загрузка\n\n"
        "🎁 Переходи по моей ссылке и получи бонус:\n"
        f"{ref_link}\n\n"
        "P.S. За каждого друга ты и я получаем +1 бесплатный просмотр 🔥"
    )

    # URL-encoded текст для шаринга
    encoded_text = quote(post_text)

    # Кнопки для шаринга
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📢 Поделиться в канале/группе",
                url=f"https://t.me/share/url?url={ref_link}&text={encoded_text}"
            )
        ],
        [
            InlineKeyboardButton(
                text="💬 Отправить другу",
                url=f"https://t.me/share/url?url={ref_link}"
            )
        ],
        [
            InlineKeyboardButton(
                text="📋 Скопировать ссылку",
                callback_data=f"copy_ref:{user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="↩️ Назад к VIP",
                callback_data="vip"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏠 Главное меню",
                callback_data="back_to_menu"
            )
        ]
    ])

    await callback.message.answer(post_text, reply_markup=keyboard, disable_web_page_preview=True)
    await callback.answer()


@router.callback_query(F.data.startswith("copy_ref:"))
async def copy_ref_link(callback: CallbackQuery, bot: Bot):
    """
    "Копирует" реферальную ссылку (показывает её в отдельном сообщении).
    """
    user_id = int(callback.data.split(":")[1])
    me = await bot.get_me()
    bot_username = me.username or "YourBot"
    ref_link = f"https://t.me/{bot_username}?start={user_id}"

    await callback.message.answer(
        f"🔗 <b>Ваша реферальная ссылка:</b>\n\n"
        f"<code>{ref_link}</code>\n\n"
        "Нажмите на ссылку, чтобы скопировать 👆",
        parse_mode="HTML"
    )
    await callback.answer("Ссылка отправлена!")
