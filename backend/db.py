import sqlite3
from typing import Optional, Dict

DB_PATH = 'app_data.db'

SCHEMA_USERS = '''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);
'''

def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(SCHEMA_USERS)
        conn.commit()


def get_user_by_username(username: str) -> Optional[Dict]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = ?', (username.strip().lower(),))
        row = cur.fetchone()
        return dict(row) if row else None


def create_user(username: str, password_hash: str) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username, password_hash))
        conn.commit()
        return cur.lastrowid