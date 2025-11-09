import os
import logging
from aiogram.types import FSInputFile
from aiogram import Bot

from keyboards.video_kb import favorites_kb
from utils.db import get_film_row_by_title, is_favorite

logger = logging.getLogger(__name__)


async def send_video_to_user(bot: Bot, user_id: int, title: str):
    """
    Отправляет видео пользователю и ПОД видео ставит ТОЛЬКО кнопку ⭐ Избранное.
    Никаких кнопок «Смотреть» здесь нет — они остаются только в сообщении
    «Реклама просмотрена…»
    """
    try:
        # Достаём строку полностью, чтобы знать film_id для избранного
        row = get_film_row_by_title(title)  # (id, title, description, video_url)
        if not row:
            await bot.send_message(user_id, "❌ Не удалось найти фильм.")
            logger.warning(f"Фильм '{title}' не найден в БД для пользователя {user_id}")
            return

        film_id, real_title, description, path = row

        if not path or not os.path.exists(path):
            await bot.send_message(user_id, "⚠️ Видеофайл не найден.")
            logger.error(
                f"Файл по пути '{path}' не найден для фильма '{real_title}' (user: {user_id})"
            )
            return

        # Состояние избранного и клавиатура
        fav_state = is_favorite(user_id, film_id)
        kb = favorites_kb(film_id, fav_state)

        # Отправляем видео
        video = FSInputFile(path)
        caption = f"🎬 <b>{real_title}</b>\n{description or ''}".strip()
        await bot.send_video(user_id, video=video, caption=caption, reply_markup=kb, parse_mode="HTML", supports_streaming=True, protect_content=True)

        logger.info(f"Видео '{real_title}' успешно отправлено пользователю {user_id}")

    except Exception as e:
        await bot.send_message(user_id, "🚫 Произошла ошибка при отправке фильма.")
        logger.exception(f"Ошибка при отправке фильма '{title}' пользователю {user_id}: {e}")
