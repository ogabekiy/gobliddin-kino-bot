import aiohttp
import logging
from typing import Optional, Dict, Literal, List

logger = logging.getLogger(__name__)

TMDB_API_KEY = "Your_API_KEY"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"


def _transliterate(text: str) -> str:
    """Простая транслитерация кириллицы -> латиница."""
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        ' ': ' '
    }
    result = []
    for char in text.lower():
        result.append(translit_map.get(char, char))
    return ''.join(result)


def _fix_keyboard_layout(text: str) -> str:
    """
    Конвертирует текст из неправильной раскладки.
    Например: 'vfnhbwf' -> 'матрица'
    """
    # Маппинг английской раскладки на русскую
    layout_map = {
        'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е', 'y': 'н', 'u': 'г', 'i': 'ш', 'o': 'щ', 'p': 'з',
        '[': 'х', ']': 'ъ', 'a': 'ф', 's': 'ы', 'd': 'в', 'f': 'а', 'g': 'п', 'h': 'р', 'j': 'о', 'k': 'л',
        'l': 'д', ';': 'ж', "'": 'э', 'z': 'я', 'x': 'ч', 'c': 'с', 'v': 'м', 'b': 'и', 'n': 'т',
        'm': 'ь', ',': 'б', '.': 'ю', '/': '.', '`': 'ё',
        # Заглавные буквы
        'Q': 'Й', 'W': 'Ц', 'E': 'У', 'R': 'К', 'T': 'Е', 'Y': 'Н', 'U': 'Г', 'I': 'Ш', 'O': 'Щ', 'P': 'З',
        '{': 'Х', '}': 'Ъ', 'A': 'Ф', 'S': 'Ы', 'D': 'В', 'F': 'А', 'G': 'П', 'H': 'Р', 'J': 'О', 'K': 'Л',
        'L': 'Д', ':': 'Ж', '"': 'Э', 'Z': 'Я', 'X': 'Ч', 'C': 'С', 'V': 'М', 'B': 'И', 'N': 'Т',
        'M': 'Ь', '<': 'Б', '>': 'Ю', '?': ',', '~': 'Ё',
        ' ': ' '
    }

    result = []
    for char in text:
        result.append(layout_map.get(char, char))
    return ''.join(result)


def _generate_search_variants(text: str) -> List[str]:

    variants = [text]

    # Если в тексте есть кириллица — добавляем транслитерацию
    if any(ord(c) > 127 for c in text):
        transliterated = _transliterate(text)
        if transliterated != text:
            variants.append(transliterated)

    # Если в тексте есть только латиница — пробуем исправить раскладку
    if all(ord(c) < 128 or c == ' ' for c in text):
        fixed_layout = _fix_keyboard_layout(text)
        if fixed_layout != text:
            variants.append(fixed_layout)
            # И от исправленной раскладки делаем транслитерацию обратно
            variants.append(_transliterate(fixed_layout))

    return list(dict.fromkeys(variants))


async def search_tmdb_movie(title: str, media_type: Literal["movie", "tv"] = "movie") -> Optional[Dict]:
    """
    Ищет фильм/сериал в TMDB и возвращает полную информацию.
    Поддерживает:
    - Транслитерацию (матрица -> matritsa)
    - Исправление раскладки (vfnhbwf -> матрица)

    Возвращает словарь:
    {
        'title': 'Интерстеллар',
        'original_title': 'Interstellar',
        'year': 2014,
        'description': 'Когда засуха приводит человечество к продовольственному кризису...',
        'poster_url': 'https://image.tmdb.org/t/p/w500/...',
        'rating': 8.4,
        'genres': 'фантастика, драма, приключения',
        'countries': 'США, Великобритания',
        'runtime': 169,
        'media_type': 'фильм',  # или 'сериал'
        'tmdb_id': 157336
    }
    """
    if not TMDB_API_KEY:
        logger.warning("TMDB API ключ не настроен")
        return None

    try:
        # Генерируем все варианты запроса
        queries = _generate_search_variants(title)
        logger.info(f"Варианты поиска для '{title}': {queries}")

        async with aiohttp.ClientSession() as session:
            for query in queries:
                # Поиск (пробуем и фильмы, и сериалы)
                for current_type in ["movie", "tv"]:
                    search_url = f"{TMDB_BASE_URL}/search/{current_type}"
                    search_params = {
                        "api_key": TMDB_API_KEY,
                        "query": query,
                        "language": "ru-RU"
                    }

                    async with session.get(search_url, params=search_params) as resp:
                        if resp.status != 200:
                            continue

                        data = await resp.json()
                        results = data.get("results", [])

                        if not results:
                            continue

                        # Берем первый (самый релевантный) результат
                        item = results[0]
                        item_id = item.get("id")

                        # Получаем детальную информацию
                        details_url = f"{TMDB_BASE_URL}/{current_type}/{item_id}"
                        details_params = {
                            "api_key": TMDB_API_KEY,
                            "language": "ru-RU"
                        }

                        async with session.get(details_url, params=details_params) as details_resp:
                            if details_resp.status != 200:
                                continue

                            details = await details_resp.json()

                            # Определяем название (для сериалов name, для фильмов title)
                            result_title = details.get("title") if current_type == "movie" else details.get("name")
                            original_title = details.get("original_title") if current_type == "movie" else details.get("original_name")

                            # Год выпуска
                            date_field = "release_date" if current_type == "movie" else "first_air_date"
                            release_date = details.get(date_field, "")
                            year = release_date.split("-")[0] if release_date else "Неизвестен"

                            # Жанры
                            genres = ", ".join([g["name"].lower() for g in details.get("genres", [])])

                            # Страны производства
                            countries_data = details.get("production_countries", [])
                            countries = ", ".join([c["name"] for c in countries_data[:3]])  # макс 3 страны

                            # Постер
                            poster_path = details.get("poster_path")
                            poster_url = f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else None

                            # Рейтинг (округляем до 1 знака)
                            rating = round(details.get("vote_average", 0), 1)

                            # Продолжительность (для сериалов берем среднюю длину эпизода)
                            if current_type == "movie":
                                runtime = details.get("runtime", 0)
                            else:
                                episode_runtimes = details.get("episode_run_time", [])
                                runtime = episode_runtimes[0] if episode_runtimes else 0

                            # Тип контента
                            media_type_ru = "фильм" if current_type == "movie" else "сериал"

                            # Собираем все данные
                            result = {
                                "title": result_title or title,
                                "original_title": original_title or "",
                                "year": year,
                                "description": details.get("overview", "Описание отсутствует"),
                                "poster_url": poster_url,
                                "rating": rating,
                                "genres": genres or "Не указано",
                                "countries": countries or "Не указано",
                                "runtime": runtime,
                                "media_type": media_type_ru,
                                "tmdb_id": item_id,
                                "tmdb_type": current_type  # для внутреннего использования
                            }

                            logger.info(f"Найден {media_type_ru} в TMDB: {result['title']} ({result['year']}) по запросу '{query}'")
                            return result

        logger.info(f"Контент '{title}' не найден в TMDB")
        return None

    except Exception as e:
        logger.exception(f"Ошибка при поиске '{title}' в TMDB: {e}")
        return None