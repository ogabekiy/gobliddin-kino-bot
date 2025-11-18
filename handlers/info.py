import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.main_menu import get_main_menu_keyboard

logger = logging.getLogger(__name__)
router = Router()


# ИНСТРУКЦИЯ
@router.callback_query(F.data == "help")
async def help_root(callback: CallbackQuery):
    text = (
        "📖 <b>Qo'llanma</b>\n\n"
        "• Filmni nomi bo‘yicha yoki «To‘plamlar/Filtr» orqali toping.\n"
        "• «Reklamani ko‘rish»ni bosing, so‘ng «▶️ Ko‘rish» — video chatga keladi.\n"
        "• Reklamasiz ko‘rishni xohlaysizmi? «VIP bepul» bo‘limiga qarang.\n\n"
        "Quyidan bo‘limni tanlang:"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Qanday ko'rish", callback_data="help_watch")],
        [InlineKeyboardButton(text="🎛 Filtr va qidiruv", callback_data="help_filter")],
        [InlineKeyboardButton(text="❓ FAQ", callback_data="help_faq")],
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_menu")],
    ])
    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "help_watch")
async def help_watch(callback: CallbackQuery):
    text = (
        "▶️ <b>Filmni qanday ko'rish</b>\n\n"
        "1) Film kartasini oching → «📺 Reklamani ko‘rish».\n"
        "2) Mini-ilovada 2 ta reklama ekranini kuting va «Ko'rishga qaytish» tugmasini bosing.\n"
        "3) Bot «Video ko'rish 👇» xabarini yuboradi. «▶️ Ko'rish» tugmasini bosing — video chatga keladi.\n\n"
        "Agar reklama yuklanmasa — mini oynani qayta oching."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Qo'llanmaga qaytish", callback_data="help")],
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_menu")],
    ])
    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "help_filter")
async def help_filter(callback: CallbackQuery):
    text = (
        "🎛️ <b>Filtr va qidiruv</b>\n\n"
        "• To‘liq nomni kiriting, masalan <code>Interstellar</code>.\n"
        "• «Filtr» — janr/yil/sifatni tanlang.\n"
        "• «To‘plamlar» — mavzular bo‘yicha tayyor kolleksiyalar.\n\n"
        "Topilmadi? Alternativ yozuvni (lotin yoki kirill) sinab ko‘ring."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔎 Qidirishni boshlash", callback_data="search")],
        [InlineKeyboardButton(text="↩️ Qo'llanmaga qaytish", callback_data="help")],
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_menu")],
    ])
    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "help_faq")
async def help_faq(callback: CallbackQuery):
    text = (
        "❓ <b>FAQ</b>\n\n"
        "• <b>Video kelmadi</b> — internetni tekshiring va «Reklamani ko‘rish»ni qayta bajaring.\n"
        "• <b>Reklamasiz ko'rmoqchiman</b> — «VIP bepul» bo‘limini oching.\n"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Qo'llanmaga qaytish", callback_data="help")],
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_menu")],
    ])
    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()


#  VIP БЕСПЛАТНО
@router.callback_query(F.data == "vip")
async def vip_root(callback: CallbackQuery):
    text = (
        "👑 <b>VIP bepul</b>\n\n"
        "VIP nima beradi:\n"
        "• Reklamasiz ko‘rish\n"
        "Bepul olish uchun — quyidan tanlang:"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💡 Qanday olish", callback_data="vip_how")],
        [InlineKeyboardButton(text="🎁 Do‘stlarni taklif qilish", callback_data="vip_invite")],
        [InlineKeyboardButton(text="ℹ️ Afzalliklar", callback_data="vip_benefits")],
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_menu")],
    ])
    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "vip_how")
async def vip_how(callback: CallbackQuery):
    text = (
        "💡 <b>VIPni bepul olish</b>\n\n"
        "1) 10 ta do‘stni shaxsiy havola orqali taklif qiling.\n"
        "2) Har biri havola orqali botni ishga tushirishi va asosiy menyuni ochishi kerak.\n"
        "3) Shu bajarilgach — VIP avtomatik tarzda “Sozlamalar” bo‘limida faollashadi."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Do‘stlarni taklif qilish", callback_data="vip_invite")],
        [InlineKeyboardButton(text="↩️ VIPga qaytish", callback_data="vip")],
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_menu")],
    ])
    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()

@router.callback_query(F.data == "vip_invite")
async def vip_invite(callback: CallbackQuery):
    me = await callback.bot.get_me()
    username = me.username or "YourBot"
    user_id = callback.from_user.id
    deep_link = f"https://t.me/{username}?start={user_id}"

    text = (
        "🎁 <b> Do‘stlarni taklif qilish</b>\n\n"
        "Ushbu havolani do‘stlaringizga yuboring. 10 kishi botni havola orqali ishga tushirganda,"
        "VIP avtomatik faollashadi.\n\n"
        f"<code>{deep_link}</code>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Do‘stlar bilan ulashish", callback_data="ref_share")],  # <- НОВАЯ КНОПКА
        [InlineKeyboardButton(text="↩️ VIPga qaytish", callback_data="vip")],
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_menu")],
    ])
    await callback.message.answer(text, reply_markup=kb, disable_web_page_preview=True)
    await callback.answer()

@router.callback_query(F.data == "vip_benefits")
async def vip_benefits(callback: CallbackQuery):
    text = (
        "ℹ️ <b>VIP afzalliklari</b>\n\n"
        "• Reklamasiz tomosha \n"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ VIPga qaytish", callback_data="vip")],
        [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="back_to_menu")],
    ])
    await callback.message.answer(text, reply_markup=kb)
    await callback.answer()
