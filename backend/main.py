#!/usr/bin/env python3
"""
Simple Flask backend for Edullm authentication
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import hmac
import os
import base64
import json
from datetime import datetime, timedelta, timezone

# Support Postgres when DATABASE_URL is present
DATABASE_URL = os.environ.get('DATABASE_URL')
IS_POSTGRES = bool(DATABASE_URL)
if IS_POSTGRES:
    import psycopg2
    import psycopg2.extras

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database setup
DB_PATH = 'app_data.db'


def _adjust_query(query: str) -> str:
    """Convert sqlite-style placeholders (?) to psycopg2 (%s) when using Postgres."""
    if IS_POSTGRES:
        return query.replace('?', '%s')
    return query


def _connect():
    """Return a DB connection for sqlite or postgres depending on environment."""
    if IS_POSTGRES:
        # psycopg2 accepts the full DATABASE_URL
        return psycopg2.connect(DATABASE_URL)
    return sqlite3.connect(DB_PATH)

# PBKDF2 parameters
_ITERATIONS = 100_000
_SALT_BYTES = 16

# JWT-like minimal token (HS256) without external deps
_SECRET = os.environ.get('EDULLM_JWT_SECRET', 'dev-secret-change-me')

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')

def _b64url_decode(data: str) -> bytes:
    padding = '=' * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode(data + padding)

def hash_password(password: str) -> str:
    salt = os.urandom(_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, _ITERATIONS)
    return f"{_b64url(salt)}:{_b64url(dk)}"

def verify_password(password: str, stored: str) -> bool:
    try:
        salt_b64, hash_b64 = stored.split(':', 1)
        salt = _b64url_decode(salt_b64)
        expected = _b64url_decode(hash_b64)
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, _ITERATIONS)
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False

def create_access_token(payload: dict, expires_minutes: int = 60) -> str:
    header = {'alg': 'HS256', 'typ': 'JWT'}
    exp = datetime.now(tz=timezone.utc) + timedelta(minutes=expires_minutes)
    body = {**payload, 'exp': int(exp.timestamp())}
    header_b64 = _b64url(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    body_b64 = _b64url(json.dumps(body, separators=(',', ':')).encode('utf-8'))
    to_sign = f"{header_b64}.{body_b64}".encode('utf-8')
    sig = hmac.new(_SECRET.encode('utf-8'), to_sign, hashlib.sha256).digest()
    token = f"{header_b64}.{body_b64}.{_b64url(sig)}"
    return token

def decode_token(token: str) -> dict:
    try:
        header_b64, body_b64, sig_b64 = token.split('.')
        to_sign = f"{header_b64}.{body_b64}".encode('utf-8')
        expected_sig = _b64url(hmac.new(_SECRET.encode('utf-8'), to_sign, hashlib.sha256).digest())
        if not hmac.compare_digest(expected_sig, sig_b64):
            raise ValueError('Invalid signature')
        body = json.loads(_b64url_decode(body_b64))
        if int(body.get('exp', 0)) < int(datetime.now(tz=timezone.utc).timestamp()):
            raise ValueError('Token expired')
        return body
    except Exception:
        raise ValueError('Invalid token')

def init_db():
    if IS_POSTGRES:
        with _connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT now()
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS history (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    subject TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT now(),
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );
                """
            )
            conn.commit()
    else:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                );
            ''')
            conn.commit()

def get_user_by_username(username: str):
    username_clean = username.strip().lower()
    if IS_POSTGRES:
        with _connect() as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(_adjust_query('SELECT * FROM users WHERE username = ?'), (username_clean,))
            row = cur.fetchone()
            return dict(row) if row else None
    else:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute('SELECT * FROM users WHERE username = ?', (username_clean,))
            row = cur.fetchone()
            return dict(row) if row else None

def create_user(username: str, password_hash: str) -> int:
    username_clean = username.strip().lower()
    if IS_POSTGRES:
        with _connect() as conn:
            cur = conn.cursor()
            cur.execute(_adjust_query('INSERT INTO users (username, password_hash) VALUES (?, ?) RETURNING id'), (username_clean, password_hash))
            new_id = cur.fetchone()[0]
            conn.commit()
            return int(new_id)
    else:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', (username_clean, password_hash))
            conn.commit()
            return cur.lastrowid

def save_user_history(user_id: int, subject: str, question: str, answer: str):
    if IS_POSTGRES:
        with _connect() as conn:
            cur = conn.cursor()
            cur.execute(_adjust_query('INSERT INTO history (user_id, subject, question, answer) VALUES (?, ?, ?, ?)'), (user_id, subject, question, answer))
            conn.commit()
    else:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    subject TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                );
            ''')
            cur.execute('INSERT INTO history (user_id, subject, question, answer) VALUES (?, ?, ?, ?)', 
                       (user_id, subject, question, answer))
            conn.commit()

def get_user_history(user_id: int, limit: int = 20):
    if IS_POSTGRES:
        with _connect() as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(_adjust_query('SELECT * FROM history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?'), (user_id, limit))
            return [dict(row) for row in cur.fetchall()]
    else:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute('SELECT * FROM history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?', (user_id, limit))
            return [dict(row) for row in cur.fetchall()]

# Initialize database on startup
init_db()

@app.route('/health', methods=['GET'])
def health():
    return {'status': 'ok'}

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('username') or not data.get('password'):
        return {'error': 'Username and password required'}, 400
    
    username = data['username'].strip().lower()
    existing = get_user_by_username(username)
    if existing:
        return {'error': 'Username already exists'}, 409
    
    pwd_hash = hash_password(data['password'])
    create_user(username, pwd_hash)
    return {'ok': True, 'message': 'Account created'}, 201

@app.route('/auth/login', methods=['POST'])
def login():
    # Support both JSON and form data
    if request.is_json:
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
    
    if not username or not password:
        return {'error': 'Username and password required'}, 400
    
    user = get_user_by_username(username.strip().lower())
    if not user or not verify_password(password, user['password_hash']):
        return {'error': 'Invalid credentials'}, 401
    
    token = create_access_token({'sub': str(user['id']), 'username': user['username']})
    return {'access_token': token, 'token_type': 'bearer'}

@app.route('/auth/me', methods=['GET'])
def me():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return {'error': 'Missing or invalid authorization header'}, 401
    
    token = auth_header[7:]  # Remove "Bearer "
    try:
        payload = decode_token(token)
        return {'id': int(payload['sub']), 'username': payload['username']}
    except ValueError as e:
        return {'error': str(e)}, 401

@app.route('/admin/users', methods=['GET'])
def admin_users():
    """Admin endpoint to view all users (for debugging)"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute('SELECT id, username, created_at FROM users ORDER BY created_at DESC')
            users = [dict(row) for row in cur.fetchall()]
            return {
                'total_users': len(users),
                'users': users,
                'database_path': DB_PATH
            }
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/history/save', methods=['POST'])
def save_history():
    """Save user question/answer history"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return {'error': 'Missing or invalid authorization header'}, 401
    
    token = auth_header[7:]  # Remove "Bearer "
    try:
        payload = decode_token(token)
        user_id = int(payload['sub'])
    except ValueError as e:
        return {'error': str(e)}, 401
    
    data = request.get_json()
    if not data or not all(k in data for k in ['subject', 'question', 'answer']):
        return {'error': 'Missing required fields: subject, question, answer'}, 400
    
    try:
        save_user_history(user_id, data['subject'], data['question'], data['answer'])
        return {'ok': True, 'message': 'History saved'}, 201
    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/history', methods=['GET'])
def get_history():
    """Get user history"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return {'error': 'Missing or invalid authorization header'}, 401
    
    token = auth_header[7:]  # Remove "Bearer "
    try:
        payload = decode_token(token)
        user_id = int(payload['sub'])
    except ValueError as e:
        return {'error': str(e)}, 401
    
    limit = request.args.get('limit', 20, type=int)
    try:
        history = get_user_history(user_id, limit)
        return {'history': history}
    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)