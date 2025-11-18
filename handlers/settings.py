from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from utils.db import get_user_info

router = Router()

@router.callback_query(F.data == "settings")
async def show_settings(callback: CallbackQuery, bot: Bot):
    # Если в БД есть авто-апгрейд по инвайтам — применим
    try:
        from utils.db import upgrade_to_vip_if_needed
        upgrade_to_vip_if_needed(callback.from_user.id)
    except Exception:
        # если функции нет — просто продолжаем отображать
        pass

    user_id = callback.from_user.id
    info = get_user_info(user_id)
    if not info:
        await callback.message.answer("⚠️ Foydalanuvchi topilmadi.")
        return

    status = "VIP ✅" if info["is_vip"] else "VIP emas ❌"
    invites = info["invites_count"]
    views = info["free_views"]

    me = await bot.get_me()
    bot_username = me.username
    ref_link = f"https://t.me/{bot_username}?start={user_id}"

    text = (
        f"⚙️ <b>Sizning sozlamalaringiz</b>\n\n"
        f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        f"👑 <b>Status:</b> {status}\n"
        f"🙌 <b>Taklif qilingan do'stlar:</b> {invites} / 10\n"
        f"🎁 <b>Bepul ko'rishlar:</b> {views}\n\n"
        f"🔗 <b>Sizning referal havolangiz:</b>\n<code>{ref_link}</code>\n\n"
        f"10 do'stni taklif qiling va reklamasiz VIP-kirish oling 😉"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Do'stlar bilan ulashish", callback_data="ref_share")],
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_menu")]
    ])

    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()
