from aiogram import Bot
from config import CHANNELS
from aiogram.exceptions import TelegramBadRequest

async def is_subscribed(bot: Bot, user_id: int) -> bool:
    """
    Foydalanuvchi CHANNELS ichidagi kanallarga obuna bo'lganmi tekshiradi.
    Hozir faqat bitta kanal tekshiriladi.
    """
    for channel_id in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status in ("left", "kicked"):
                return False
        except TelegramBadRequest:
            return False
        except Exception:
            return False
    return True
