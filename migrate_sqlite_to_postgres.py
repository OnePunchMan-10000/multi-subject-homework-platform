"""Migrate data from local SQLite `app_data.db` to Postgres defined by DATABASE_URL.

Usage:
  Set environment variable DATABASE_URL to the target Postgres URL, then run:
    python migrate_sqlite_to_postgres.py
"""
import os
import sqlite3
from urllib.parse import urlparse

DATABASE_URL = os.environ.get("DATABASE_URL")
SQLITE_FILE = "app_data.db"

if not DATABASE_URL:
    raise SystemExit("Please set DATABASE_URL environment variable to your Postgres URL.")

import psycopg2


def pg_conn_from_url(url):
    return psycopg2.connect(url)


def ensure_tables_pg(conn):
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
      id SERIAL PRIMARY KEY,
      username TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS history (
      id SERIAL PRIMARY KEY,
      user_id INTEGER NOT NULL REFERENCES users(id),
      subject TEXT NOT NULL,
      question TEXT NOT NULL,
      answer TEXT,
      created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    );
    """)
    conn.commit()


def migrate():
    # Read from sqlite
    sconn = sqlite3.connect(SQLITE_FILE)
    scur = sconn.cursor()
    try:
        scur.execute("SELECT id, username, password_hash, created_at FROM users")
        users = scur.fetchall()
    except Exception:
        users = []

    pconn = pg_conn_from_url(DATABASE_URL)
    ensure_tables_pg(pconn)
    pcur = pconn.cursor()

    # Insert users mapping old id -> new id
    id_map = {}
    for old_id, username, password_hash, created_at in users:
        pcur.execute(
            "INSERT INTO users (username, password_hash, created_at) VALUES (%s,%s,%s) ON CONFLICT (username) DO UPDATE SET password_hash = EXCLUDED.password_hash RETURNING id",
            (username, password_hash, created_at),
        )
        new_id = pcur.fetchone()[0]
        id_map[old_id] = new_id
    pconn.commit()

    # Migrate history
    try:
        scur.execute("SELECT id, user_id, subject, question, answer, created_at FROM history")
        history_rows = scur.fetchall()
    except Exception:
        history_rows = []

    for _id, user_id, subject, question, answer, created_at in history_rows:
        new_user_id = id_map.get(user_id)
        if new_user_id is None:
            continue
        pcur.execute(
            "INSERT INTO history (user_id, subject, question, answer, created_at) VALUES (%s,%s,%s,%s,%s)",
            (new_user_id, subject, question, answer, created_at),
        )
    pconn.commit()
    pcur.close()
    pconn.close()
    sconn.close()
    print("Migration finished.")


if __name__ == "__main__":
    migrate()


