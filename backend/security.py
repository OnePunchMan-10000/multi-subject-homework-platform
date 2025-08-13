from datetime import datetime, timedelta, timezone
from typing import Dict
from pydantic import BaseModel
import hashlib, hmac, os, base64, json
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# PBKDF2 parameters
_ITERATIONS = 100_000
_SALT_BYTES = 16

# JWT-like minimal token (HS256) without external deps
_SECRET = os.environ.get('EDULLM_JWT_SECRET', 'dev-secret-change-me')
_ALG = 'HS256'


class Token(BaseModel):
    access_token: str
    token_type: str


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


def create_access_token(payload: Dict, expires_minutes: int = 60) -> str:
    header = {'alg': _ALG, 'typ': 'JWT'}
    exp = datetime.now(tz=timezone.utc) + timedelta(minutes=expires_minutes)
    body = {**payload, 'exp': int(exp.timestamp())}
    header_b64 = _b64url(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    body_b64 = _b64url(json.dumps(body, separators=(',', ':')).encode('utf-8'))
    to_sign = f"{header_b64}.{body_b64}".encode('utf-8')
    sig = hmac.new(_SECRET.encode('utf-8'), to_sign, hashlib.sha256).digest()
    token = f"{header_b64}.{body_b64}.{_b64url(sig)}"
    return token


def decode_token(token: str) -> Dict:
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid token')


_oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')


def get_current_user(token: str = Depends(_oauth2_scheme)) -> Dict:
    body = decode_token(token)
    return {'id': int(body['sub']), 'username': body['username']}


