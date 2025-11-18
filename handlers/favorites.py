from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards.video_kb import favorites_kb
from utils.db import toggle_favorite, is_favorite  # id-based helpers (favorites(user_id, film_id))

router = Router()

@router.callback_query(F.data.startswith("fav:"))
async def toggle_fav_under_video(callback: CallbackQuery):
    """
    Обрабатывает кнопку под ВИДЕО с форматом callback_data = 'fav:<film_id>'.
    """
    data = callback.data.split(":", 1)
    if len(data) != 2 or not data[1].isdigit():
        await callback.answer("Noto'g'ri ma'lumotlar.", show_alert=True)
        return

    film_id = int(data[1])
    user_id = callback.from_user.id

    state = toggle_favorite(user_id, film_id)  # True => добавлено, False => удалено
    kb = favorites_kb(film_id, state)

    try:
        await callback.message.edit_reply_markup(reply_markup=kb)
    except Exception:
        pass

    await callback.answer("Sevimlilarga qo'shildi" if state else "Sevimlilardan o'chirildi")
