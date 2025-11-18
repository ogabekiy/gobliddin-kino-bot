import os
import logging
from aiogram.types import FSInputFile
from aiogram import Bot

from keyboards.video_kb import favorites_kb
from utils.db import get_film_row_by_title, is_favorite

logger = logging.getLogger(__name__)


async def send_video_to_user(bot: Bot, user_id: int, title: str):
    """
    Foydalanuvchiga videoni yuboradi va video ostiga faqat ⭐ Sevimlilar tugmasini qo'yadi.
    Bu yerda «Videoni ko'rish» tugmalari yo'q — ular faqat xabarda
    "Reklama ko'rildi…" qoladi.
    """
    try:
        # Dastlab butun satrni olib film_id ni aniqlaymiz (sevimlilar uchun)
        row = get_film_row_by_title(title)  # (id, title, description, video_url)
        if not row:
            await bot.send_message(user_id, "❌ Film topilmadi.")
            logger.warning(f"Film '{title}' foydalanuvchi {user_id} uchun bazada topilmadi")
            return

        film_id, real_title, description, path = row

        if not path or not os.path.exists(path):
            await bot.send_message(user_id, "⚠️ Video fayl topilmadi.")
            logger.error(
                f"'{path}' yo'lida '{real_title}' filmi uchun fayl topilmadi (user: {user_id})"
            )
            return

        # Sevimlilar holati va klaviatura
        fav_state = is_favorite(user_id, film_id)
        kb = favorites_kb(film_id, fav_state)

        # Videoni yuborish
        video = FSInputFile(path)
        caption = f"🎬 <b>{real_title}</b>\n{description or ''}".strip()
        await bot.send_video(user_id, video=video, caption=caption, reply_markup=kb, parse_mode="HTML", supports_streaming=True, protect_content=True)

        logger.info(f"Video '{real_title}' foydalanuvchi {user_id} ga muvaffaqiyatli yuborildi")

    except Exception as e:
        await bot.send_message(user_id, "🚫 Filmni yuborishda xatolik yuz berdi.")
        logger.exception(f"Film '{title}' ni foydalanuvchi {user_id} ga yuborishda xatolik: {e}")
