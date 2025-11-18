from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio
import logging
from aiohttp import web
from uuid import uuid4

from handlers import get_movie_by_code
from handlers import start, search, watch, settings, info, collections, filter, favorites, favlist, referral
from config import BOT_TOKEN, CHANNEL_LINK
from utils.debug_middleware import DebugMiddleware
from middleware.check_subscription import CheckSubscriptionMiddleware
from aiogram.types import (
    InlineQuery, InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# ---------- Middleware qo'shish ----------
dp.message.middleware(CheckSubscriptionMiddleware())
dp.callback_query.middleware(CheckSubscriptionMiddleware())

# ixtiyoriy — loglar
# dp.message.middleware(DebugMiddleware())
# dp.callback_query.middleware(DebugMiddleware())
# dp.errors.middleware(DebugMiddleware())
# dp.update.outer_middleware(DebugMiddleware())

for name in ("aiogram", "aiogram.dispatcher", "aiogram.event",
             "aiohttp.access", "aiosqlite"):
    logging.getLogger(name).setLevel(logging.WARNING)

# ---------- Routers qo'shish ----------
dp.include_router(get_movie_by_code.router)
dp.include_router(start.router)
dp.include_router(referral.router)
dp.include_router(favlist.router)
dp.include_router(search.router)
dp.include_router(watch.router)
dp.include_router(favorites.router)
dp.include_router(settings.router)
dp.include_router(info.router)
dp.include_router(collections.router)
dp.include_router(filter.router)

# ---------- INLINE MODE ----------
@dp.inline_query()
async def inline_search_handler(inline_query: InlineQuery):
    """
    Inline qidiruvni ishlash (@botname matn).
    Ko'rsatadi: tur (film/serial), yil, janrlar, mamlakat, reyting.
    """
    try:
        from utils.db import search_films_by_title_or_tags
        from utils.tmdb_api import search_tmdb_movie

        query = inline_query.query.strip()
        results = []

        if not query:
            from utils.db import get_random_films
            films = get_random_films(limit=10)

            for title, _ in films:
                try:
                    tmdb_data = await search_tmdb_movie(title)
                    if tmdb_data:
                        desc_short = f"{tmdb_data['media_type']} | {tmdb_data['genres']} | {tmdb_data['year']}"
                        full_desc = (
                            f"🎬 <b>{tmdb_data['title']}</b>\n"
                            f"📺 {tmdb_data['media_type']} | {tmdb_data['countries']} | {tmdb_data['year']}\n"
                            f"⭐️ {tmdb_data['rating']}/10 | 🎭 {tmdb_data['genres']}\n\n"
                            f"{tmdb_data['description']}"
                        )
                        poster_url = tmdb_data['poster_url']
                    else:
                        desc_short = "Tavsif yo'q"
                        full_desc = f"🎬 <b>{title}</b>\n\nTavsif mavjud emas"
                        poster_url = "https://via.placeholder.com/150"

                    results.append(
                        InlineQueryResultArticle(
                            id=str(uuid4()),
                            title=tmdb_data['title'] if tmdb_data else title,
                            description=desc_short,
                            thumbnail_url=poster_url,
                            input_message_content=InputTextMessageContent(
                                message_text=full_desc,
                                parse_mode="HTML"
                            ),
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="▶️ Ko'rish", callback_data=f"watch:{title}")],
                                [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="back_to_menu")]
                            ])
                        )
                    )
                except Exception as e:
                    logger.exception(f"Film '{title}'ni qayta ishlashda xato: {e}")
                    continue

        else:
            films = search_films_by_title_or_tags(query, limit=20)
            logger.info(f"📊 Inline qidiruv '{query}': DBda {len(films)} ta film topildi")

            if not films:
                results.append(
                    InlineQueryResultArticle(
                        id=str(uuid4()),
                        title="Hech narsa topilmadi 😔",
                        description="Boshqa so'rov kiriting",
                        thumbnail_url="https://via.placeholder.com/150?text=Not+Found",
                        input_message_content=InputTextMessageContent(
                            message_text="❌ <b>Hech narsa topilmadi</b>\n\nBoshqa so'rov kiriting yoki menyu tugmalaridan foydalaning.",
                            parse_mode="HTML"
                        ),
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="back_to_menu")]
                        ])
                    )
                )
            else:
                for film_id, title, db_description in films:
                    try:
                        tmdb_data = await search_tmdb_movie(title)
                        if tmdb_data:
                            desc_short = f"{tmdb_data['media_type']} | {tmdb_data['genres']} | {tmdb_data['year']}"
                            full_desc = (
                                f"🎬 <b>{tmdb_data['title']}</b>\n"
                                f"📺 {tmdb_data['media_type']} | {tmdb_data['countries']} | {tmdb_data['year']}\n"
                                f"⭐️ {tmdb_data['rating']}/10 | 🎭 {tmdb_data['genres']}\n\n"
                                f"{tmdb_data['description']}"
                            )
                            poster_url = tmdb_data['poster_url']
                        else:
                            desc_short = db_description[:50] if db_description else "Tavsif yo'q"
                            full_desc = f"🎬 <b>{title}</b>\n\n{db_description or 'Tavsif mavjud emas'}"
                            poster_url = "https://via.placeholder.com/150"

                        results.append(
                            InlineQueryResultArticle(
                                id=str(uuid4()),
                                title=tmdb_data['title'] if tmdb_data else title,
                                description=desc_short,
                                thumbnail_url=poster_url,
                                input_message_content=InputTextMessageContent(
                                    message_text=full_desc,
                                    parse_mode="HTML"
                                ),
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                    [InlineKeyboardButton(text="▶️ Ko'rish", callback_data=f"watch:{title}")],
                                    [InlineKeyboardButton(text="🏠 Bosh menyu", callback_data="back_to_menu")]
                                ])
                            )
                        )
                    except Exception as e:
                        logger.exception(f"Film '{title}'ni qayta ishlashda xato: {e}")
                        continue

        await inline_query.answer(
            results=results[:50] if results else [],
            cache_time=10,
            is_personal=True
        )

    except Exception as e:
        logger.exception(f"Inline search handlerda tanqidiy xato: {e}")
        await inline_query.answer(results=[], cache_time=1)


# ---------- Web server qismlari ----------
def _cors(resp: web.StreamResponse) -> web.StreamResponse:
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return resp

async def handle_options(request: web.Request):
    return _cors(web.Response())

async def webapp_done(request: web.Request):
    try:
        data = await request.json()
        user_id = data.get("user_id")
        title   = data.get("title")

        if not user_id or not title:
            return _cors(web.json_response({"ok": False, "error": "user_id and title required"}, status=400))

        text = (
            "<b>Reklama ko'rildi.</b>\n\n"
            "Videoni ko'rish 👇"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Videoni ko'rish", callback_data=f"play:{title}")]
        ])

        await bot.send_message(
            chat_id=int(user_id),
            text=text,
            reply_markup=kb,
            disable_web_page_preview=True
        )

        return _cors(web.json_response({"ok": True}))
    except Exception as e:
        logger.exception("webapp_done xatosi")
        return _cors(web.json_response({"ok": False, "error": str(e)}, status=500))


async def run_web_server():
    app = web.Application()
    app.router.add_route("OPTIONS", "/webapp/done", handle_options)
    app.router.add_post("/webapp/done", webapp_done)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=8080)
    await site.start()
    logger.info("Web server started on http://0.0.0.0:8080")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot ishga tushdi. To'xtatish uchun Ctrl+C bosing.")
    await asyncio.gather(
        dp.start_polling(bot),
        run_web_server()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Dastur qo'lda to'xtatildi.")
