from __future__ import annotations

import aiosqlite
from typing import List, Tuple, Optional

from .db import DB_PATH


async def _get_film_id_by_title(conn: aiosqlite.Connection, title: str) -> Optional[int]:
    cur = await conn.execute("SELECT id FROM films WHERE title = ? LIMIT 1", (title,))
    row = await cur.fetchone()
    await cur.close()
    return row[0] if row else None


async def add_favorite(user_id: int, title: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as conn:
        film_id = await _get_film_id_by_title(conn, title)
        if film_id is None:
            return False
        # защита от дублей — PRIMARY KEY (user_id, film_id)
        try:
            await conn.execute(
                "INSERT OR IGNORE INTO favorites(user_id, film_id) VALUES (?, ?)",
                (user_id, film_id),
            )
            await conn.commit()
            return True
        except Exception:
            return False


async def remove_favorite(user_id: int, title: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as conn:
        film_id = await _get_film_id_by_title(conn, title)
        if film_id is None:
            return False
        cur = await conn.execute(
            "DELETE FROM favorites WHERE user_id = ? AND film_id = ?",
            (user_id, film_id),
        )
        await conn.commit()
        return cur.rowcount > 0


async def is_favorite(user_id: int, title: str) -> bool:
    async with aiosqlite.connect(DB_PATH) as conn:
        film_id = await _get_film_id_by_title(conn, title)
        if film_id is None:
            return False
        cur = await conn.execute(
            "SELECT 1 FROM favorites WHERE user_id = ? AND film_id = ? LIMIT 1",
            (user_id, film_id),
        )
        row = await cur.fetchone()
        await cur.close()
        return row is not None


async def list_favorites(user_id: int) -> List[Tuple[str, str]]:
    """
    Возвращает список [(title, description)] для пользователя.
    """
    async with aiosqlite.connect(DB_PATH) as conn:
        cur = await conn.execute(
            """
            SELECT f.title, f.description
            FROM favorites fa
            JOIN films f ON f.id = fa.film_id
            WHERE fa.user_id = ?
            ORDER BY f.title COLLATE NOCASE
            """,
            (user_id,),
        )
        rows = await cur.fetchall()
        await cur.close()
    return [(r[0], r[1] or "") for r in rows]
