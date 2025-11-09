import logging
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)

from config import CHANNEL_LINKS
from keyboards.main_menu import get_main_menu_keyboard
from utils.check_subs import is_subscribed
from utils.db import register_user

logger = logging.getLogger(__name__)
router = Router()


# /start с параметром (реферал) — регистрируем + проверка подписки
@router.message(CommandStart(deep_link=True))
async def start_deeplink(message: Message, state: FSMContext, command: CommandStart):
    await state.clear()
    user_id = message.from_user.id

    # пригласивший
    inviter_id = None
    try:
        if command.args:
            inviter_id = int(command.args)
            if inviter_id == user_id:
                inviter_id = None
    except Exception:
        inviter_id = None

    register_user(user_id, invited_by=inviter_id)

    # Сохраняем флаг, что пользователь пришел по реферальной ссылке
    await state.update_data(from_referral=True)

    text = (
        "<b>🎉 Добро пожаловать!</b>\n\n"
        "Ты пришёл по реферальной ссылке и получаешь <b>1 бесплатный просмотр без рекламы!</b>\n\n"
        "Чтобы активировать бонус, подпишись на наши каналы 👇"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Канал 1", url=CHANNEL_LINKS[0])],
        #       [InlineKeyboardButton(text="🎬 Канал 2", url=CHANNEL_LINKS[1])],
        [InlineKeyboardButton(text="✅ Я подписался", callback_data="check_subs_referral")]
    ])

    await message.answer(text, reply_markup=keyboard)


# Обычный /start — всегда «сброс» в главное меню
@router.message(CommandStart())
async def start_plain(message: Message, state: FSMContext):
    await state.clear()
    register_user(message.from_user.id)  # на всякий случай
    await message.answer("🏠 Главное меню:", reply_markup=get_main_menu_keyboard())


# /menu — быстрый вход в главное меню
@router.message(Command("menu"))
async def menu_cmd(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🏠 Главное меню:", reply_markup=get_main_menu_keyboard())


# Проверка подписок для обычного входа
@router.callback_query(F.data == "check_subs")
async def check_subscriptions(callback: CallbackQuery, bot: Bot):
    user_id = callback.from_user.id
    if await is_subscribed(bot, user_id):
        await callback.message.edit_text(
            "<b>Отлично, подписка подтверждена!</b>\n\n"
            "🔍 Для поиска используй кнопки ниже или отправь в сообщении название кино.\n\n"
            "Возникнут вопросы – нажми «Инструкция».",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await callback.answer("Вы не подписаны на все каналы 😢", show_alert=True)


# Проверка подписок для реферального входа
@router.callback_query(F.data == "check_subs_referral")
async def check_subscriptions_referral(callback: CallbackQuery, bot: Bot, state: FSMContext):
    user_id = callback.from_user.id
    if await is_subscribed(bot, user_id):
        # Показываем раздел VIP с информацией о бонусе
        text = (
            "👑 <b>Поздравляем!</b>\n\n"
            "✅ Подписка подтверждена!\n"
            "🎁 Ты получил <b>1 бесплатный просмотр без рекламы</b>!\n\n"
            "Что это значит:\n"
            "• При выборе любого фильма ты сможешь посмотреть его сразу, без просмотра рекламы\n"
            "• После использования бонуса потребуется смотреть рекламу\n\n"
            "💡 Хочешь смотреть <b>всегда без рекламы</b>?\n"
            "Пригласи 10 друзей и получи VIP-доступ навсегда!"
        )

        me = await bot.get_me()
        username = me.username or "YourBot"
        ref_link = f"https://t.me/{username}?start={user_id}"

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🎁 Пригласить друзей", callback_data="vip_invite")],
            [InlineKeyboardButton(text="💡 Как получить VIP навсегда", callback_data="vip_how")],
            [InlineKeyboardButton(text="🎬 Начать смотреть", callback_data="back_to_menu")],
        ])

        await callback.message.edit_text(text, reply_markup=kb)
        await state.clear()  # Очищаем флаг реферала
    else:
        await callback.answer("Вы не подписаны на все каналы 😢", show_alert=True)


# Возврат в меню по inline-кнопке
@router.callback_query(F.data == "back_to_menu")
async def back_to_main(callback: CallbackQuery):
    await callback.message.answer("🏠 Главное меню:", reply_markup=get_main_menu_keyboard())
    await callback.answer()

