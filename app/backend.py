import requests
import streamlit as st

try:
    BACKEND_URL = st.secrets.get('BACKEND_URL', 'http://127.0.0.1:8000')
except:
    BACKEND_URL = 'http://127.0.0.1:8000'


def backend_register(username: str, password: str) -> tuple[bool, str]:
    try:
        r = requests.post(f"{BACKEND_URL}/auth/register", json={"username": username, "password": password}, timeout=6)
        if r.status_code in (200, 201):
            return True, r.json().get('message', 'Account created')
        # Attempt to read common error message
        try:
            return False, r.json().get('detail', r.text)
        except Exception:
            return False, r.text
    except requests.RequestException as e:
        return False, str(e)


def backend_login(username: str, password: str) -> tuple[bool, str]:
    try:
        # backend expects form data for OAuth2PasswordRequestForm
        r = requests.post(f"{BACKEND_URL}/auth/login", data={"username": username, "password": password}, timeout=6)
        if r.status_code == 200:
            return True, r.json().get('access_token')
        try:
            return False, r.json().get('detail', r.text)
        except Exception:
            return False, r.text
    except requests.RequestException as e:
        return False, str(e)


def backend_get_me(token: str) -> tuple[bool, dict | str]:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(f"{BACKEND_URL}/auth/me", headers=headers, timeout=6)
        if r.status_code == 200:
            return True, r.json()
        try:
            return False, r.json().get('detail', r.text)
        except Exception:
            return False, r.text
    except requests.RequestException as e:
        return False, str(e)


def backend_save_history(subject: str, question: str, answer: str) -> bool:
    """Save question/answer to backend history"""
    try:
        token = st.session_state.get("access_token")
        if not token:
            return False
        
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "subject": subject,
            "question": question,
            "answer": answer
        }
        r = requests.post(f"{BACKEND_URL}/history/save", json=data, headers=headers, timeout=6)
        return r.status_code in (200, 201)
    except:
        return False


def backend_get_history(limit: int = 20) -> list:
    """Get user history from backend"""
    try:
        token = st.session_state.get("access_token")
        if not token:
            return []
        
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(f"{BACKEND_URL}/history?limit={limit}", headers=headers, timeout=6)
        if r.status_code == 200:
            data = r.json()
            return data.get("history", [])
        return []
    except:
        return []


