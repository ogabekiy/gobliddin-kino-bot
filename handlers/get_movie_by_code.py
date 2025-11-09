from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
import os

from keyboards.main_menu import get_main_menu_keyboard  # 🔹 main menu import

load_dotenv()
PRIVATE_CHANNEL = int(os.getenv("PRIVATE_CHANNEL"))

router = Router()

class MovieCode(StatesGroup):
    waiting_for_code = State()


@router.callback_query(F.data == "get_movie_by_code")
async def ask_code(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🎞 Введите код фильма (ID):")
    await state.set_state(MovieCode.waiting_for_code)
    await callback.answer()


@router.message(MovieCode.waiting_for_code)
async def send_movie_copy(message: Message, state: FSMContext):
    code = message.text.strip()
    await state.clear()

    try:
        # Filmni PRIVATE_CHANNEL dan nusxalab yuboramiz
        await message.bot.copy_message(
            chat_id=message.chat.id,
            from_chat_id=PRIVATE_CHANNEL,
            message_id=int(code)
        )

        # 🔹 Keyin foydalanuvchini asosiy menuga qaytaramiz
        await message.answer(
            "🏠 Главное меню:",
            reply_markup=get_main_menu_keyboard()
        )

    except Exception as e:
        await message.answer(
            "❌ Ошибка при получении фильма. Проверьте код и попробуйте снова.",
            reply_markup=get_main_menu_keyboard()
        )
        print("Error while copying message:", e)
