import logging
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import CHANNEL_LINK
from keyboards.main_menu import get_main_menu_keyboard
from utils.check_subs import is_subscribed
from utils.db import register_user

logger = logging.getLogger(__name__)
router = Router()


# ---------- ODDIY START ----------
@router.message(CommandStart(deep_link=False))
async def start_plain(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    user_id = message.from_user.id

    register_user(user_id)

    # obuna tekshirish
    if not await is_subscribed(bot, user_id):
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                # Asosiy Telegram kanal (shart)
                [InlineKeyboardButton(text="📢 Kanalga obuna bo‘lish", url=CHANNEL_LINK)],
                # Instagram faqat ko‘rsatish
                [InlineKeyboardButton(text="📸 Instagram", url="https://www.instagram.com/gobliddin_kino")],
                # Obuna bo'ldim tugmasi
                [InlineKeyboardButton(text="✅ Obuna bo‘ldim", callback_data="check_subs")]
            ]
        )
        return await message.answer(
            "Iltimos Botdan to'liq foydalanish uchun quyidagi kanallarga obuna bo'ling! 👇",
            reply_markup=keyboard
        )

    await message.answer("🏠 Asosiy menyu:", reply_markup=get_main_menu_keyboard())



@router.callback_query(F.data == "check_subs")
async def check_subscriptions(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id

    if await is_subscribed(bot, user_id):
        await callback.message.edit_text(
            "<b>Ajoyib! Obuna tasdiqlandi!</b>",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await callback.answer("Hali obuna bo‘lmagansiz!", show_alert=True)


# ---------- REFERAL START ----------
@router.message(CommandStart(deep_link=True))
async def start_deeplink(message: Message, state: FSMContext, command: CommandStart, bot: Bot):
    await state.clear()

    user_id = message.from_user.id
    inviter_id = None

    if command.args:
        try:
            inviter_id = int(command.args)
            if inviter_id == user_id:
                inviter_id = None
        except:
            inviter_id = None

    register_user(user_id, invited_by=inviter_id)
    await state.update_data(from_referral=True)

    text = (
        "<b>🎉 Xush kelibsiz!</b>\n\n"
        "Siz referal havolasi orqali keldingiz.\n"
        "Bonusni olish uchun kanalga obuna bo‘ling 👇"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Kanal", url=CHANNEL_LINK)],
        [InlineKeyboardButton(text="✅ Obuna bo‘ldim", callback_data="check_subs_ref")]
    ])

    await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data == "check_subs_ref")
async def check_subscriptions_ref(callback: CallbackQuery, bot: Bot, state: FSMContext):
    user_id = callback.from_user.id

    if await is_subscribed(bot, user_id):
        text = (
            "👑 <b>Obunangiz tasdiqlandi!</b>\n\n"
            "🎁 Sizga 1 ta reklamasiz ko‘rish berildi.\n"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎬 Boshlash", callback_data="back_to_menu")],
        ])

        await callback.message.edit_text(text, reply_markup=kb)
        await state.clear()
    else:
        await callback.answer("Hali obuna bo‘lmagansiz!", show_alert=True)


@router.callback_query(F.data == "back_to_menu")
async def back_to_main(callback: CallbackQuery):
    await callback.message.answer("🏠 Asosiy menyu:", reply_markup=get_main_menu_keyboard())
    await callback.answer()
