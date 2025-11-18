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
        "👋 Salom!\n\n"
        "🎬 Men filmlar va seriallarni ko‘rish uchun zo‘r bot topdim!\n\n"
        "✨ Ichida nimalar bor:\n"
        "🎥 Filmlarning ulkan to‘plami\n"
        "📺 Barcha janrdagi seriallar\n"
        "🆓 Bepul tomosha \n"
        "⚡️ Tez yuklash\n\n"
        "🎁 Mening havolam orqali o‘t va bonus ol:\n"
        f"{ref_link}\n\n"
        "P.S. Har bir taklif qilingan do‘st uchun sen ham, men ham +1 ta bepul ko‘rish olamiz. 🔥"
    )

    # URL-encoded текст для шаринга
    encoded_text = quote(post_text)

    # Кнопки для шаринга
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📢 Kanal/Guruhda ulashish",
                url=f"https://t.me/share/url?url={ref_link}&text={encoded_text}"
            )
        ],
        [
            InlineKeyboardButton(
                text="💬 Do‘stga yuborish",
                url=f"https://t.me/share/url?url={ref_link}"
            )
        ],
        [
            InlineKeyboardButton(
                text="📋 Havolani nusxalash",
                callback_data=f"copy_ref:{user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="↩️ VIPga qaytish",
                callback_data="vip"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏠 Asosiy menyu",
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
        f"🔗 <b>Sizning referal havolangiz:</b>\n\n"
        f"<code>{ref_link}</code>\n\n"
        "Nusxalash uchun havolani bosing 👆",
        parse_mode="HTML"
    )
    await callback.answer("Havola yuborildi!")
