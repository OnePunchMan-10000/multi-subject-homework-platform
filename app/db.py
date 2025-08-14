import sqlite3
import os
import hashlib
import base64
from datetime import datetime
import secrets as pysecrets

DB_PATH = "app_data.db"

def init_db() -> None:
    """Create tables if they do not exist."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        conn.commit()


def get_or_create_user_from_email(email: str, display_name: str | None = None) -> tuple[bool, int | None, str]:
    """Find user by email-as-username; create if missing.

    Returns (ok, user_id, message).
    """
    if not email:
        return False, None, "Email not provided"
    username = email.strip().lower()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE username=?", (username,))
            row = cur.fetchone()
            if row:
                return True, row[0], "Signed in."
            # Create with random password
            random_pwd = pysecrets.token_urlsafe(24)
            pwd_hash = _hash_password(random_pwd)
            cur.execute(
                "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
                (username, pwd_hash, datetime.utcnow().isoformat()),
            )
            conn.commit()
            return True, cur.lastrowid, "Account created via OAuth."
    except sqlite3.Error as e:
        return False, None, f"Database error: {str(e)}"


def _hash_password(password: str) -> str:
    """Return salted hash using PBKDF2-HMAC-SHA256 as salt:hash (base64)."""
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return f"{base64.b64encode(salt).decode()}:{base64.b64encode(dk).decode()}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt_b64, hash_b64 = stored.split(":", 1)
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return hashlib.sha256(dk).digest() == hashlib.sha256(expected).digest()
    except Exception:
        return False


def register_user(username: str, password: str) -> tuple[bool, str]:
    username = username.strip().lower()
    if not username or not password:
        return False, "Username and password are required."
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE username=?", (username,))
            if cur.fetchone():
                return False, "Username already exists."
            pwd_hash = _hash_password(password)
            cur.execute(
                "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
                (username, pwd_hash, datetime.utcnow().isoformat()),
            )
            conn.commit()
            return True, "Account created. Please log in."
    except sqlite3.Error as e:
        return False, f"Database error: {str(e)}"


def authenticate_user(username: str, password: str) -> tuple[bool, int | None, str]:
    username = username.strip().lower()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, password_hash FROM users WHERE username=?", (username,))
            row = cur.fetchone()
            if not row:
                return False, None, "Invalid username or password."
            user_id, password_hash = row
            if _verify_password(password, password_hash):
                return True, user_id, "Login successful."
            return False, None, "Invalid username or password."
    except sqlite3.Error as e:
        return False, None, f"Database error: {str(e)}"


def save_history(user_id: int, subject: str, question: str, answer: str | None) -> None:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            # Store only the question by default; keep answer nullable for future features
            cur.execute(
                """
                INSERT INTO history (user_id, subject, question, answer, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, subject, question, None, datetime.utcnow().isoformat()),
            )
            conn.commit()
    except sqlite3.Error:
        pass


def load_history(user_id: int, limit: int = 20) -> list[tuple]:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT id, subject, question, answer, created_at
                FROM history
                WHERE user_id=?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, limit),
            )
            return cur.fetchall() or []
    except sqlite3.Error:
        return []


