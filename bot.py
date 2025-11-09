from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio
import logging
from aiohttp import web
from uuid import uuid4
from handlers import get_movie_by_code
from config import BOT_TOKEN
from handlers import start, search, watch, settings, info, collections, filter, favorites, favlist, referral
from utils.debug_middleware import DebugMiddleware
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


# опционально — логи
# dp.message.middleware(DebugMiddleware())
# dp.callback_query.middleware(DebugMiddleware())
# dp.errors.middleware(DebugMiddleware())
# dp.update.outer_middleware(DebugMiddleware())

for name in ("aiogram", "aiogram.dispatcher", "aiogram.event",
             "aiohttp.access", "aiosqlite"):
    logging.getLogger(name).setLevel(logging.WARNING)


# INLINE MODE
@dp.inline_query()
async def inline_search_handler(inline_query: InlineQuery):
    """
    Обработка inline поиска (@botname текст).
    Показывает: тип (фильм/сериал), год, жанры, страну, рейтинг.
    """
    try:
        from utils.db import search_films_by_title_or_tags
        from utils.tmdb_api import search_tmdb_movie

        query = inline_query.query.strip()
        results = []

        if not query:
            # Если запрос пустой - показываем фильмы из своей БД
            from utils.db import get_random_films
            films = get_random_films(limit=10)

            for title, _ in films:
                # Для каждого фильма из БД получаем данные из TMDB
                try:
                    tmdb_data = await search_tmdb_movie(title)

                    if tmdb_data:
                        # Короткое описание для превью
                        desc_short = f"{tmdb_data['media_type']} | {tmdb_data['genres']} | {tmdb_data['year']}"

                        # Полное описание в сообщении
                        full_desc = (
                            f"🎬 <b>{tmdb_data['title']}</b>\n"
                            f"📺 {tmdb_data['media_type']} | {tmdb_data['countries']} | {tmdb_data['year']}\n"
                            f"⭐️ {tmdb_data['rating']}/10 | 🎭 {tmdb_data['genres']}\n\n"
                            f"{tmdb_data['description']}"
                        )
                        poster_url = tmdb_data['poster_url']
                    else:
                        # Если TMDB не нашел - берем из своей БД
                        desc_short = "Нет описания"
                        full_desc = f"🎬 <b>{title}</b>\n\nОписание отсутствует"
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
                                [InlineKeyboardButton(text="▶️ Смотреть", callback_data=f"watch:{title}")],
                                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")]
                            ])
                        )
                    )
                except Exception as e:
                    logger.exception(f"Ошибка обработки фильма '{title}': {e}")
                    continue

        else:
            # Ищем по запросу СНАЧАЛА в своей БД (чтобы знать, что у нас есть видео)
            films = search_films_by_title_or_tags(query, limit=20)
            logger.info(f"📊 Inline поиск '{query}': найдено {len(films)} фильмов в БД")

            if not films:
                # Если ничего не найдено — показываем заглушку
                results.append(
                    InlineQueryResultArticle(
                        id=str(uuid4()),
                        title="Ничего не найдено 😔",
                        description="Попробуйте ввести другой запрос",
                        thumbnail_url="https://via.placeholder.com/150?text=Not+Found",
                        input_message_content=InputTextMessageContent(
                            message_text="❌ <b>Ничего не найдено</b>\n\nПопробуйте ввести другой запрос или воспользуйтесь кнопками меню.",
                            parse_mode="HTML"
                        ),
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")]
                        ])
                    )
                )
            else:
                # Для каждого найденного фильма получаем данные из TMDB
                for film_id, title, db_description in films:
                    try:
                        tmdb_data = await search_tmdb_movie(title)

                        if tmdb_data:
                            # Короткое описание для превью
                            desc_short = f"{tmdb_data['media_type']} | {tmdb_data['genres']} | {tmdb_data['year']}"

                            # Полное описание в сообщении
                            full_desc = (
                                f"🎬 <b>{tmdb_data['title']}</b>\n"
                                f"📺 {tmdb_data['media_type']} | {tmdb_data['countries']} | {tmdb_data['year']}\n"
                                f"⭐️ {tmdb_data['rating']}/10 | 🎭 {tmdb_data['genres']}\n\n"
                                f"{tmdb_data['description']}"
                            )
                            poster_url = tmdb_data['poster_url']
                        else:
                            # Fallback на данные из своей БД
                            desc_short = db_description[:50] if db_description else "Нет описания"
                            full_desc = f"🎬 <b>{title}</b>\n\n{db_description or 'Описание отсутствует'}"
                            poster_url = "https://https://some_link_on_picture"

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
                                    [InlineKeyboardButton(text="▶️ Смотреть", callback_data=f"watch:{title}")],
                                    [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_menu")]
                                ])
                            )
                        )
                    except Exception as e:
                        logger.exception(f"Ошибка обработки фильма '{title}': {e}")
                        continue

        # ВАЖНО: всегда отвечаем, даже если results пустой
        await inline_query.answer(
            results=results[:50] if results else [
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="Ошибка загрузки 😔",
                    description="Попробуйте еще раз",
                    thumbnail_url="https://some_link_on_error_picture" ,
                    input_message_content=InputTextMessageContent(
                        message_text="⚠️ Произошла ошибка при поиске. Попробуйте еще раз.",
                        parse_mode="HTML"
                    )
                )
            ],
            cache_time=10,
            is_personal=True
        )

    except Exception as e:
        logger.exception(f"Критическая ошибка в inline_search_handler: {e}")
        # В случае критической ошибки всё равно отвечаем
        await inline_query.answer(
            results=[
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title="Ошибка сервера 😔",
                    description="Попробуйте позже",
                    thumbnail_url="https://some_link_on_error_picture",
                    input_message_content=InputTextMessageContent(
                        message_text="⚠️ Произошла критическая ошибка. Попробуйте позже.",
                        parse_mode="HTML"
                    )
                )
            ],
            cache_time=1
        )


# CORS helpers
def _cors(resp: web.StreamResponse) -> web.StreamResponse:
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return resp

async def handle_options(request: web.Request):
    return _cors(web.Response())

# WebApp backend: /webapp/done
async def webapp_done(request: web.Request):
    """
    POST /webapp/done
    JSON: {"user_id": 123456789, "title": "Матрица"}
    """
    try:
        data = await request.json()
        user_id = data.get("user_id")
        title   = data.get("title")

        logger.info(f"[WEBAPP_DONE->MSG] data={data}")

        if not user_id or not title:
            return _cors(web.json_response({"ok": False, "error": "user_id and title required"}, status=400))

        text = (
            "<b>Реклама просмотрена.</b>\n\n"
            "👉 <a href='https://t.me/ВАШ_КОНТАКТ_ДЛЯ_РЕКЛАМЫ'>Заказать рекламу</a>\n\n"
            "Смотреть видео 👇"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="▶️ Смотреть видео", callback_data=f"play:{title}")]
        ])

        await bot.send_message(
            chat_id=int(user_id),
            text=text,
            reply_markup=kb,
            disable_web_page_preview=True
        )

        return _cors(web.json_response({"ok": True}))
    except Exception as e:
        logger.exception("webapp_done error")
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
    logger.info("Бот запущен. Нажмите Ctrl+C для остановки.")
    await asyncio.gather(
        dp.start_polling(bot),
        run_web_server()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Программа остановлена вручную.")