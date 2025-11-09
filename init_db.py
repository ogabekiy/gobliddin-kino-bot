import sqlite3

conn = sqlite3.connect("films.db")
cursor = conn.cursor()

# Таблица фильмов
cursor.execute('''
CREATE TABLE IF NOT EXISTS films (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    tags TEXT,
    video_url TEXT
)
''')

# Таблица пользователя
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    is_vip INTEGER DEFAULT 0,
    invited_by INTEGER,
    invites_count INTEGER DEFAULT 0,
    free_views INTEGER DEFAULT 0
)
''')

# Таблица избранного
cursor.execute('''
CREATE TABLE IF NOT EXISTS favorites (
    user_id INTEGER,
    film_id INTEGER,
    PRIMARY KEY (user_id, film_id)
)
''')

conn.commit()
conn.close()
print("База инициализирована.")
