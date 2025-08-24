import sqlite3
import os
import hashlib
import base64
from datetime import datetime
import secrets as pysecrets

# Optional Postgres support via DATABASE_URL
DATABASE_URL = os.environ.get("DATABASE_URL")
IS_POSTGRES = bool(DATABASE_URL)

if IS_POSTGRES:
    import psycopg2
    from urllib.parse import urlparse

DB_PATH = "app_data.db"

# Performance/security tradeoff: reduce PBKDF2 iterations for faster login while
# remaining backward-compatible with existing hashes. New hashes include the
# iteration count as a prefix so we can migrate users transparently on login.
PBKDF2_ITERATIONS = 30000  # new default for hashing (faster)
LEGACY_PBKDF2_ITERATIONS = 100_000  # previous value used in older hashes


def _adjust_query(query: str) -> str:
    """Convert sqlite-style placeholders (?) to psycopg2 (%s) when using Postgres."""
    if IS_POSTGRES:
        return query.replace("?", "%s")
    return query


def _connect():
    """Return a DB connection for sqlite or postgres depending on environment."""
    if IS_POSTGRES:
        # psycopg2 accepts the full DATABASE_URL
        return psycopg2.connect(DATABASE_URL)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    """Create tables if they do not exist."""
    if IS_POSTGRES:
        with _connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS history (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    subject TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
                """
            )
            conn.commit()
    else:
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
                    answer TEXT,
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
        with _connect() as conn:
            cur = conn.cursor()
            q = _adjust_query("SELECT id FROM users WHERE username=?")
            cur.execute(q, (username,))
            row = cur.fetchone()
            if row:
                # psycopg2 returns tuples; sqlite returns tuples
                return True, row[0], "Signed in."
            # Create with random password
            random_pwd = pysecrets.token_urlsafe(24)
            pwd_hash = _hash_password(random_pwd)
            q = _adjust_query("INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)")
            cur.execute(q, (username, pwd_hash, datetime.utcnow().isoformat()))
            conn.commit()
            # get last id
            if IS_POSTGRES:
                cur.execute("SELECT id FROM users WHERE username=%s", (username,))
                new_id = cur.fetchone()[0]
            else:
                new_id = cur.lastrowid
            return True, new_id, "Account created via OAuth."
    except Exception as e:
        return False, None, f"Database error: {str(e)}"


def _hash_password(password: str, iterations: int = PBKDF2_ITERATIONS) -> str:
    """Return salted hash using PBKDF2-HMAC-SHA256 with iteration count.

    Stored format: "{iterations}${salt_b64}:{dk_b64}". Older entries may be in the
    legacy format "{salt_b64}:{dk_b64}" which implies LEGACY_PBKDF2_ITERATIONS.
    """
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"{iterations}${base64.b64encode(salt).decode()}:{base64.b64encode(dk).decode()}"


def _verify_password(password: str, stored: str) -> tuple[bool, int]:
    """Verify password and return (matches, iterations_used).

    This returns the iteration count used to verify so callers can decide whether to
    re-hash the password using the newer (faster) iterations and update the DB.
    """
    try:
        # Detect new stored format with iterations prefix
        if "$" in stored:
            iter_str, rest = stored.split("$", 1)
            iterations = int(iter_str)
            salt_b64, hash_b64 = rest.split(":", 1)
        else:
            iterations = LEGACY_PBKDF2_ITERATIONS
            salt_b64, hash_b64 = stored.split(":", 1)

        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(hash_b64)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        matches = hashlib.sha256(dk).digest() == hashlib.sha256(expected).digest()
        return matches, iterations
    except Exception:
        return False, 0


def register_user(username: str, password: str) -> tuple[bool, str]:
    username = username.strip().lower()
    if not username or not password:
        return False, "Username and password are required."
    try:
        with _connect() as conn:
            cur = conn.cursor()
            q = _adjust_query("SELECT id FROM users WHERE username=?")
            cur.execute(q, (username,))
            if cur.fetchone():
                return False, "Username already exists."
            pwd_hash = _hash_password(password)
            q = _adjust_query("INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)")
            cur.execute(q, (username, pwd_hash, datetime.utcnow().isoformat()))
            conn.commit()
            return True, "Account created. Please log in."
    except Exception as e:
        return False, f"Database error: {str(e)}"


def authenticate_user(username: str, password: str) -> tuple[bool, int | None, str]:
    username = username.strip().lower()
    try:
        with _connect() as conn:
            cur = conn.cursor()
            q = _adjust_query("SELECT id, password_hash FROM users WHERE username=?")
            cur.execute(q, (username,))
            row = cur.fetchone()
            if not row:
                return False, None, "Invalid username or password."
            user_id, password_hash = row[0], row[1]

            matches, iterations_used = _verify_password(password, password_hash)
            if matches:
                # To avoid adding latency on login due to an extra DB write,
                # we do NOT re-hash and update the stored password here.
                # Migration to a new hash format can be done in a background job.
                return True, int(user_id), "Login successful."
            return False, None, "Invalid username or password."
    except Exception as e:
        return False, None, f"Database error: {str(e)}"


def save_history(user_id: int, subject: str, question: str, answer: str | None) -> None:
    try:
        with _connect() as conn:
            cur = conn.cursor()
            q = _adjust_query("INSERT INTO history (user_id, subject, question, answer, created_at) VALUES (?, ?, ?, ?, ?)")
            cur.execute(q, (user_id, subject, question, answer, datetime.utcnow().isoformat()))
            conn.commit()
    except Exception:
        pass


def load_history(user_id: int, limit: int = 20) -> list[tuple]:
    try:
        with _connect() as conn:
            cur = conn.cursor()
            q = _adjust_query("SELECT id, subject, question, answer, created_at FROM history WHERE user_id=? ORDER BY id DESC LIMIT ?")
            cur.execute(q, (user_id, limit))
            rows = cur.fetchall() or []
            return rows
    except Exception:
        return []


