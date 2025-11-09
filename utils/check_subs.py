from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from config import CHANNELS

async def is_subscribed(bot: Bot, user_id: int) -> bool:
    # Временный мок на период разработки
    return True  # TODO: Реализовать проверку подписки по get_chat_member

# async def is_subscribed(bot: Bot, user_id: int) -> bool:
#     """
#     Проверяет, подписан ли пользователь на все каналы из списка CHANNELS.
#     """
#     for channel_id in CHANNELS:
#         try:
#             member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
#             if member.status in ("left", "kicked"):
#                 return False
#         except TelegramBadRequest:
#             return False  # если канал не найден или другой баг
#     return True
