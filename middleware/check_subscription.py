from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from utils.check_subs import is_subscribed
from config import CHANNEL_LINK

class CheckSubscriptionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        bot = data["bot"]
        user_id = None
        chat = None
        message_type = None

        if isinstance(event, Message):
            user_id = event.from_user.id
            chat = event
            message_type = "message"
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            chat = event.message
            message_type = "callback"

        if user_id is not None:
            if not await is_subscribed(bot, user_id):
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        # Asosiy kanalga obuna bo'lish shart
                        [InlineKeyboardButton(text="📢 Kanalga obuna bo‘lish", url=CHANNEL_LINK)],
                        # Instagram faqat ko'rsatish uchun
                        [InlineKeyboardButton(text="📸 Instagram", url="https://www.instagram.com/gobliddin_kino")],
                        # Obuna bo'ldim tugmasi
                        [InlineKeyboardButton(text="✅ Obuna bo‘ldim", callback_data="check_subs")]
                    ]
                )

                await chat.answer(
                    "<b>Iltimos Botdan to'liq foydalanish uchun quyidagi kanallarga obuna bo'ling! 👇</b>",
                    reply_markup=keyboard
                )

                if message_type == "message":
                    return  # Xabarni davom ettirmaslik
                elif message_type == "callback":
                    await event.answer(
                        "Iltimos Botdan to'liq foydalanish uchun quyidagi kanallarga obuna bo'ling! 👇",
                        show_alert=True
                    )
                    return

        return await handler(event, data)
