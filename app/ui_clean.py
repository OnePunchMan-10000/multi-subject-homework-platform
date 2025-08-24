import streamlit as st
from app.backend import BACKEND_URL
import requests

def render_global_css():
    st.markdown(r"""
    <style>
      :root{ --gold: #d4af37; }
      .landing { background: linear-gradient(135deg,#0b0b0d,#221f1a); padding:36px 12px; color:#fff; }
      .brand { font-size:44px; font-weight:800; letter-spacing:2px; }
      .subtitle { opacity:0.9; margin-top:8px; }
      .cta { margin-top:18px; }
      .feature-grid { display:flex; gap:14px; margin-top:20px; }
      .feature-card { background: rgba(255,255,255,0.03); padding:16px; border-radius:10px; flex:1 }
    </style>
    """, unsafe_allow_html=True)


def render_landing_page():
    render_global_css()
    st.markdown("""
    <div class='landing'>
      <div style='max-width:980px;margin:0 auto;text-align:center;'>
        <div style='font-size:48px;'>👑</div>
        <div class='brand'>EDULLM</div>
        <div class='subtitle'>Demo · Your AI-powered study companion</div>
        <div style='margin-top:8px; color:rgba(255,255,255,0.8)'>Clear, step-by-step homework solutions with concise explanations.</div>
        <div class='cta'>
          <button onclick="window.streamlitRerun && window.streamlitRerun()" class='stButton'>Start Learning</button>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # safe fallback functional button
    if st.button('Start Learning (open login)', key='start_learning_clean'):
        st.session_state['show_login'] = True
        st.rerun()


def auth_ui():
    """Minimal, fast auth UI. Returns True on success."""
    st.header('Welcome back!')

    # Use a Streamlit form to ensure a single reliable submit action.
    with st.form(key='login_form'):
        username = st.text_input('Email or username')
        password = st.text_input('Password', type='password')
        submit = st.form_submit_button('Sign In')

    if submit:
        if st.session_state.get('auth_in_progress'):
            st.info('Login already in progress...')
            return False

        if not username or not password:
            st.error('Please enter both fields.')
            return False

        st.session_state['auth_in_progress'] = True
        try:
            with st.spinner('Signing in...'):
                r = requests.post(f"{BACKEND_URL}/auth/login", json={"username": username, "password": password}, timeout=5)
        except Exception as e:
            st.error(f'Connection failed: {e}')
            st.session_state['auth_in_progress'] = False
            return False
        finally:
            st.session_state['auth_in_progress'] = False

        if r.status_code == 200:
            try:
                data = r.json()
            except Exception:
                st.error('Invalid response from server.')
                return False

            token = data.get('access_token') or data.get('token')
            if token:
                st.success(f'✅ Welcome, {username}!')
                st.session_state['access_token'] = token
                st.session_state['user_id'] = username
                st.session_state['username'] = username
                st.session_state['show_login'] = False
                return True
            else:
                st.warning(data.get('detail') or data.get('message') or 'Invalid credentials')
                return False
        else:
            st.error('Server error. Try again later.')
            return False

    return False


def render_footer():
    st.markdown("""
    <div style='text-align:center; opacity:0.7; margin-top:24px;'>© 2025 by Praveen</div>
    """, unsafe_allow_html=True)


