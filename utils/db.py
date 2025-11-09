import sqlite3
import aiosqlite
import random
from collections import Counter
import logging

DB_PATH = "films.db"

def _conn():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)  # Увеличили таймаут

    conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
    conn.execute("PRAGMA synchronous=NORMAL")  # Быстрее запись
    conn.execute("PRAGMA cache_size=-64000")  # 64MB кэш
    conn.execute("PRAGMA temp_store=MEMORY")  # Временные данные в RAM
    conn.execute("PRAGMA mmap_size=268435456")  # 256MB memory-mapped I/O

    return conn

logger = logging.getLogger(__name__)


def _transliterate_to_latin(text: str) -> str:
    """Транслитерация: кириллица → латиница"""
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
    }
    result = []
    for char in text.lower():
        result.append(translit_map.get(char, char))
    return ''.join(result)


def _transliterate_to_cyrillic(text: str) -> str:
    """Транслитерация: латиница → кириллица (ОБРАТНАЯ)"""
    text_lower = text.lower()

    # Сначала заменяем многобуквенные сочетания, потом одиночные
    replacements = [
        ('shch', 'щ'), ('sch', 'щ'), ('zh', 'ж'), ('kh', 'х'),
        ('ch', 'ч'), ('sh', 'ш'), ('yo', 'ё'), ('yu', 'ю'),
        ('ya', 'я'), ('ts', 'ц'),
        ('a', 'а'), ('b', 'б'), ('v', 'в'), ('g', 'г'), ('d', 'д'),
        ('e', 'е'), ('z', 'з'), ('i', 'и'), ('y', 'й'), ('k', 'к'),
        ('l', 'л'), ('m', 'м'), ('n', 'н'), ('o', 'о'), ('p', 'п'),
        ('r', 'р'), ('s', 'с'), ('t', 'т'), ('u', 'у'), ('f', 'ф'),
        ('h', 'х'), ('c', 'к'),
    ]

    result = text_lower
    for lat, cyr in replacements:
        result = result.replace(lat, cyr)

    return result


def _fix_keyboard_layout(text: str) -> str:
    """Конвертирует текст из неправильной раскладки (vfnhbwf -> матрица)."""
    layout_map = {
        'q': 'й', 'w': 'ц', 'e': 'у', 'r': 'к', 't': 'е', 'y': 'н', 'u': 'г', 'i': 'ш', 'o': 'щ', 'p': 'з',
        '[': 'х', ']': 'ъ', 'a': 'ф', 's': 'ы', 'd': 'в', 'f': 'а', 'g': 'п', 'h': 'р', 'j': 'о', 'k': 'л',
        'l': 'д', ';': 'ж', "'": 'э', 'z': 'я', 'x': 'ч', 'c': 'с', 'v': 'м', 'b': 'и', 'n': 'т',
        'm': 'ь', ',': 'б', '.': 'ю', '/': '.', '`': 'ё',
        'Q': 'Й', 'W': 'Ц', 'E': 'У', 'R': 'К', 'T': 'Е', 'Y': 'Н', 'U': 'Г', 'I': 'Ш', 'O': 'Щ', 'P': 'З',
        '{': 'Х', '}': 'Ъ', 'A': 'Ф', 'S': 'Ы', 'D': 'В', 'F': 'А', 'G': 'П', 'H': 'Р', 'J': 'О', 'K': 'Л',
        'L': 'Д', ':': 'Ж', '"': 'Э', 'Z': 'Я', 'X': 'Ч', 'C': 'С', 'V': 'М', 'B': 'И', 'N': 'Т',
        'M': 'Ь', '<': 'Б', '>': 'Ю', '?': ',', '~': 'Ё',
        ' ': ' '
    }
    return ''.join(layout_map.get(c, c) for c in text)


def _generate_search_variants_db(text: str) -> list[str]:
    """Генерирует ВСЕ варианты запроса для поиска в БД."""
    variants = set()
    text_stripped = text.strip()

    if not text_stripped:
        return []

    # Добавляем оригинал
    variants.add(text_stripped)

    # Добавляем варианты с разным регистром
    variants.add(text_stripped.lower())
    variants.add(text_stripped.upper())
    variants.add(text_stripped.capitalize())

    # Проверяем наличие кириллицы и латиницы
    has_cyrillic = any('\u0400' <= c <= '\u04FF' for c in text_stripped)
    has_latin = any('a' <= c.lower() <= 'z' for c in text_stripped)

    # Если есть кириллица → добавляем транслит в латиницу
    if has_cyrillic:
        to_latin = _transliterate_to_latin(text_stripped)
        if to_latin and to_latin != text_stripped.lower():
            variants.add(to_latin)
            variants.add(to_latin.capitalize())

    # Если есть латиница → добавляем транслит в кириллицу
    if has_latin:
        to_cyrillic = _transliterate_to_cyrillic(text_stripped)
        if to_cyrillic and to_cyrillic != text_stripped.lower():
            variants.add(to_cyrillic)
            variants.add(to_cyrillic.capitalize())
            variants.add(to_cyrillic.upper())

    # Если только латиница → пробуем исправить раскладку
    if has_latin and not has_cyrillic:
        fixed_layout = _fix_keyboard_layout(text_stripped)
        if fixed_layout != text_stripped:
            variants.add(fixed_layout)
            variants.add(fixed_layout.capitalize())
            variants.add(fixed_layout.upper())
            # Для исправленной раскладки тоже добавляем транслит
            fixed_latin = _transliterate_to_latin(fixed_layout)
            if fixed_latin:
                variants.add(fixed_latin)
                variants.add(fixed_latin.capitalize())

    # Убираем пустые и возвращаем список
    return [v for v in variants if v and len(v) > 0]



# def _conn():
#    return sqlite3.connect(DB_PATH)

def _norm_tag(tag: str) -> str:
    return tag.strip().lower()



def get_film_by_title(query: str):
    """(title, description, video_url) — для старых мест кода."""
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT title, description, video_url FROM films WHERE title LIKE ? COLLATE NOCASE LIMIT 1",
        (f"%{query}%",),
    )
    row = cur.fetchone()
    conn.close()
    return row


def get_film_row_by_title(query: str):
    """(id, title, description, video_url) — нужен id."""
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, description, video_url FROM films WHERE title LIKE ? COLLATE NOCASE LIMIT 1",
        (f"%{query}%",),
    )
    row = cur.fetchone()
    conn.close()
    return row


def get_film_by_id(film_id: int):
    """(id, title, description, video_url) по id."""
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, description, video_url FROM films WHERE id = ?",
        (film_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def get_films_by_tag(tag: str, limit: int = 10):
    tag = _norm_tag(tag)
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT title, description
        FROM films
        WHERE instr(lower(COALESCE(tags, '')), ? ) > 0
        ORDER BY id DESC
        LIMIT ?
        """,
        (tag, limit),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_random_films(limit: int = 5):
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM films")
    ids = [r[0] for r in cur.fetchall()]
    if not ids:
        conn.close()
        return []
    sample_ids = random.sample(ids, min(limit, len(ids)))
    q = ",".join("?" for _ in sample_ids)
    cur.execute(f"SELECT title, description FROM films WHERE id IN ({q})", sample_ids)
    rows = cur.fetchall()
    conn.close()
    return rows


def get_top_tags(limit: int = 12) -> list[str]:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT tags FROM films WHERE tags IS NOT NULL AND TRIM(tags) <> ''")
    all_rows = cur.fetchall()
    conn.close()

    counter = Counter()
    for (tag_line,) in all_rows:
        parts = [t.strip() for t in tag_line.split(",") if t.strip()]
        counter.update(_norm_tag(p) for p in parts)

    if not counter:
        return []
    top = [name.capitalize() for name, _ in counter.most_common(limit)]
    seen, res = set(), []
    for t in top:
        k = t.lower()
        if k not in seen:
            seen.add(k)
            res.append(t)
    return res


def search_films_by_title_or_tags(query: str, limit: int = 8):
    """
    Ищем фильмы по названию ИЛИ по тегам.
    Поддерживает:
    - Поиск по части слова (LIKE '%...%')
    - Двустороннюю транслитерацию (кириллица ↔ латиница)
    - Исправление раскладки (vfnhbwf → матрица)

    Возвращаем [(id, title, description), ...]
    """
    q = (query or "").strip()
    if not q:
        return []

    # Генерируем все варианты запроса
    variants = _generate_search_variants_db(q)
    logger.info(f"🔍 DB поиск '{q}': варианты = {variants}")

    if not variants:
        return []

    conn = _conn()
    cur = conn.cursor()

    # Собираем результаты без дубликатов
    seen_ids = set()
    all_results = []

    for variant in variants:
        like_pattern = f"%{variant}%"

        # Простой поиск без COLLATE NOCASE (т.к. мы генерируем все варианты регистра)
        cur.execute(
            """
            SELECT id, title, description
            FROM films
            WHERE title LIKE ?
               OR COALESCE(tags, '') LIKE ?
            """,
            (like_pattern, like_pattern),
        )

        rows = cur.fetchall()
        logger.info(f"  ↳ вариант '{variant}': {len(rows)} результатов")

        for row in rows:
            if row[0] not in seen_ids:
                all_results.append(row)
                seen_ids.add(row[0])

                if len(all_results) >= limit:
                    break

        if len(all_results) >= limit:
            break

    conn.close()

    result = all_results[:limit]
    logger.info(f"🔍 DB поиск '{q}': ИТОГО {len(result)} фильмов")
    return result


# Users

def register_user(user_id: int, invited_by: int | None = None):
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    if cur.fetchone():
        conn.close()
        return
    cur.execute(
        "INSERT INTO users (user_id, is_vip, invited_by, free_views, invites_count) VALUES (?,0,?,1,0)",
        (user_id, invited_by),
    )
    if invited_by:
        cur.execute(
            "UPDATE users SET invites_count = invites_count + 1, free_views = free_views + 1 WHERE user_id = ?",
            (invited_by,),
        )
        cur.execute("SELECT invites_count FROM users WHERE user_id = ?", (invited_by,))
        row = cur.fetchone()
        if row and row[0] >= 10:
            cur.execute("UPDATE users SET is_vip = 1 WHERE user_id = ?", (invited_by,))
    conn.commit()
    conn.close()


async def is_user_vip(user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT is_vip FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            return bool(row and row[0] == 1)


def get_user_info(user_id: int):
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT is_vip, invites_count, free_views FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {"is_vip": bool(row[0]), "invites_count": row[1], "free_views": row[2]}


def try_consume_free_view(user_id: int) -> bool:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT free_views FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if not row or row[0] <= 0:
        conn.close()
        return False
    cur.execute("UPDATE users SET free_views = free_views - 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True


def upgrade_to_vip_if_needed(user_id: int):
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT is_vip, invites_count FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if row and row[0] == 0 and row[1] >= 10:
        cur.execute("UPDATE users SET is_vip = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
    conn.close()


# Favorite

def is_favorite(user_id: int, film_id: int) -> bool:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM favorites WHERE user_id = ? AND film_id = ?", (user_id, film_id))
    ok = cur.fetchone() is not None
    conn.close()
    return ok


def add_favorite(user_id: int, film_id: int):
    conn = _conn()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO favorites(user_id, film_id) VALUES(?,?)", (user_id, film_id))
    conn.commit()
    conn.close()


def remove_favorite(user_id: int, film_id: int):
    conn = _conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM favorites WHERE user_id = ? AND film_id = ?", (user_id, film_id))
    conn.commit()
    conn.close()


def toggle_favorite(user_id: int, film_id: int) -> bool:
    """True => стало избранным, False => удалили из избранного."""
    if is_favorite(user_id, film_id):
        remove_favorite(user_id, film_id)
        return False
    add_favorite(user_id, film_id)
    return True


def get_favorites(user_id: int):
    """[(film_id, title, description)]"""
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT f.id, f.title, f.description
        FROM favorites fav
        JOIN films f ON f.id = fav.film_id
        WHERE fav.user_id = ?
        ORDER BY f.title COLLATE NOCASE
        """,
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows