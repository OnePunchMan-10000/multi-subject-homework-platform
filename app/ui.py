import streamlit as st
import re
import html
import secrets as pysecrets
from app.subjects import SUBJECTS
from app.backend import backend_register, backend_login, backend_get_me
from app.backend import backend_save_history
from app.db import get_or_create_user_from_email
import os
import sqlite3
import pandas as pd

# Page CSS and styling
_GLOBAL_CSS = r"""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Navigation Menu */
    .nav-menu {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 15px 25px;
        margin: 20px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    /* ... rest of CSS omitted for brevity in this file view; full CSS reproduced in original hw01.py */
</style>
"""

def render_global_css():
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)


def render_navigation():
    """Render the top navigation menu"""
    # Initialize page state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    
    # Check if user is logged in (using user_id)
    is_logged_in = bool(st.session_state.get("user_id"))
    
    # Navigation menu
    st.markdown("""
    <div class="nav-menu">
        <div style="text-align: center;">
    """, unsafe_allow_html=True)
    
    # Create navigation buttons
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    
    with col1:
        if st.button("🏠 Home", key="nav_home", help="Go to homepage"):
            st.session_state.current_page = 'home'
            st.rerun()
    
    with col2:
        if st.button("👤 Profile", key="nav_profile", help="View your profile"):
            st.session_state.current_page = 'profile'
            st.rerun()
    
    with col3:
        if st.button("📚 Subjects", key="nav_subjects", help="Browse subjects"):
            st.session_state.current_page = 'subjects'
            st.rerun()
    
    with col4:
        if st.button("ℹ️ About", key="nav_about", help="About Edullm"):
            st.session_state.current_page = 'about'
            st.rerun()
    
    with col5:
        if is_logged_in:
            if st.button("🚪 Logout", key="nav_logout", help="Sign out"):
                # Clear session
                for key in list(st.session_state.keys()):
                    if key not in ['current_page']:
                        del st.session_state[key]
                st.session_state.current_page = 'home'
                st.success("Logged out successfully!")
                st.rerun()
        else:
            if st.button("🔑 Login", key="nav_login", help="Sign in"):
                st.session_state.current_page = 'home'
                st.rerun()
    
    # Admin button (only visible when logged in)
    if is_logged_in:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔐 Admin", key="nav_admin", help="Admin database access"):
            st.session_state.current_page = 'admin'
            st.rerun()
    
    st.markdown("</div></div>", unsafe_allow_html=True)


def render_footer():
    """Render the bottom footer"""
    st.markdown("""
    <div class="app-footer">
        <div class="footer-content">
            © 2025 Edullm - Academic Assistant Pro. All rights reserved. | 
            Empowering students with AI-powered homework solutions.
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_home_page():
    """Render the homepage with subject selection"""
    st.markdown('<div class="main-header">Edullm</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Clear, step-by-step homework solutions</div>', unsafe_allow_html=True)
    
    # Subject selection
    render_subject_grid()


def render_profile_page():
    """Render the user profile page"""
    st.markdown('<div class="main-header">👤 User Profile</div>', unsafe_allow_html=True)
    
    if not st.session_state.get("user_id"):
        st.warning("Please log in to view your profile.")
        return
    
    username = st.session_state.get("username", "Unknown")
    st.markdown(f"""
    <div style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; margin: 20px 0;">
        <h3>👋 Welcome back!</h3>
        <p><strong>Username:</strong> {username}</p>
        <p><strong>Member since:</strong> 2025</p>
        <p><strong>Questions solved:</strong> Coming soon...</p>
    </div>
    """, unsafe_allow_html=True)


def render_about_page():
    """Render the about page"""
    st.markdown('<div class="main-header">ℹ️ About Edullm</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; margin: 20px 0; line-height: 1.6;">
        <h3>🎓 Your AI-Powered Academic Assistant</h3>
        
        <p><strong>Edullm</strong> is designed to help students excel in their academic journey by providing 
        clear, step-by-step solutions to homework problems across multiple subjects.</p>
        
        <h4>📚 Subjects We Cover:</h4>
        <ul>
            <li>📐 <strong>Mathematics</strong> - Algebra, Calculus, Geometry, Statistics</li>
            <li>🧪 <strong>Physics</strong> - Mechanics, Thermodynamics, Electromagnetism</li>
            <li>⚗️ <strong>Chemistry</strong> - Organic, Inorganic, Physical Chemistry</li>
            <li>🧬 <strong>Biology</strong> - Cell Biology, Genetics, Ecology</li>
            <li>💻 <strong>Computer Science</strong> - Programming, Algorithms, Data Structures</li>
            <li>📊 <strong>Economics</strong> - Micro, Macro, Econometrics</li>
            <li>📖 <strong>English</strong> - Literature, Grammar, Writing</li>
            <li>📜 <strong>History</strong> - World History, Analysis, Research</li>
            <li>🌍 <strong>Geography</strong> - Physical, Human, Environmental</li>
        </ul>
        
        <h4>✨ Features:</h4>
        <ul>
            <li>🤖 AI-powered explanations</li>
            <li>📝 Step-by-step solutions</li>
            <li>📊 Visual diagrams and graphs</li>
            <li>💾 Save your solution history</li>
            <li>🔐 Secure user accounts</li>
        </ul>
        
        <h4>🚀 Mission:</h4>
        <p>To make quality education accessible to every student by providing instant, 
        accurate, and comprehensive homework assistance.</p>
        
        <hr style="border: 1px solid rgba(255,255,255,0.3); margin: 20px 0;">
        
        <p style="text-align: center; opacity: 0.8;">
            <em>Built with ❤️ for students worldwide</em>
        </p>
    </div>
    """, unsafe_allow_html=True)


def auth_ui() -> bool:
    """Login page matching the first image design."""
    # Note: For brevity this function reproduces the original auth UI behavior.
    # It depends on backend_register/backend_login/backend_get_me and local fallback.

    login_bg_url = "https://i.pinimg.com/originals/33/ff/b4/33ffb4819b0810c8ef39bf7b4f1b4f27.jpg"
    # Hide navigation only on auth page and use a polished auth container look
    st.markdown(f"""
    <style>
    /* Hide streamlit elements and top nav on auth page */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stDeployButton {{visibility: hidden;}}
    .nav-menu {{display: none !important;}}
    
    /* Hide stray top floating rounded/shadow boxes on auth page */
    /* Targets elements inside .stApp that have both a box-shadow and border-radius style */
    .stApp div[style*="box-shadow"][style*="border-radius"] {{ display: none !important; }}
    /* Also hide any fixed-position rounded elements (common for floating headers) */
    .stApp div[style*="position: fixed"][style*="border-radius"] {{ display: none !important; }}

    .stApp {{
        background-image: url('{login_bg_url}') !important;
        background-size: cover !important; 
        background-position: center !important; 
        background-attachment: fixed !important;
    }}
    
    .auth-container {{
        background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 30px 60px rgba(2,6,23,0.6), inset 0 1px 0 rgba(255,255,255,0.02);
        backdrop-filter: blur(10px) saturate(120%);
        max-width: 720px;
        margin: 6vh auto;
        padding: 3.5rem 3rem;
        color: #ffffff;
        font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
    }}

    .brand-title {{ font-size: 48px; margin: 0 0 6px 0; font-weight: 700; color: #fff; letter-spacing: -0.5px }}
    .brand-subtitle {{ color: rgba(255,255,255,0.85); margin-top: 0; margin-bottom: 1.4rem; font-size: 16px }}

    .stButton>button, .stForm button {{ background: linear-gradient(90deg,#ff4d4f,#ff7a45); border-radius: 10px; border: none; padding: 12px 18px; color:#ffffff; font-weight:600 }}
    .stTextInput>div>div>input {{ background: rgba(10,10,10,0.25); padding: 12px 14px; border-radius: 8px; color: #fff }}
    .stTabs button[role="tab"] {{ font-weight:600 }}
    
    @media (max-width: 800px) {{
        .auth-container {{ margin: 2vh 1rem; padding: 2rem 1.5rem; max-width: 100% }}
        .brand-title {{ font-size: 32px }}
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="auth-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="brand-title">Edullm</h1>', unsafe_allow_html=True)
    st.markdown('<p class="brand-subtitle">Clear, step-by-step homework solutions</p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username", label_visibility="visible")
            password = st.text_input("Password", type="password", placeholder="Enter your password", label_visibility="visible")
            login_btn = st.form_submit_button("Login", use_container_width=True)

            if login_btn:
                if not username or not password:
                    st.error("Username and password required")
                else:
                    ok, token_or_err = backend_login(username, password)
                    if ok:
                        token = token_or_err
                        st.session_state["access_token"] = token
                        ok2, me_or_err = backend_get_me(token)
                        if ok2:
                            st.session_state["user_id"] = me_or_err.get("id")
                            st.session_state["username"] = me_or_err.get("username")
                            st.success("Logged in successfully!")
                            st.rerun()
                        else:
                            st.error(f"Login succeeded but fetching user failed: {me_or_err}")
                    else:
                        st.error(f"Login failed: {token_or_err}")

    with tab2:
        with st.form("register_form"):
            new_user = st.text_input("Username", placeholder="Choose username", key="reg_username")
            new_pass = st.text_input("Password", type="password", placeholder="Choose password", key="reg_password")
            confirm_pass = st.text_input("Confirm Password", type="password", placeholder="Confirm password", key="reg_confirm")
            register_btn = st.form_submit_button("Create Account", use_container_width=True)

            if register_btn:
                if not new_user or not new_pass:
                    st.error("Username and password required")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = backend_register(new_user, new_pass)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)

    # OAuth demo buttons (Google / GitHub)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Continue with Google", use_container_width=True, key="google_btn"):
            demo_email = st.secrets.get("GOOGLE_DEMO_EMAIL", "")
            if demo_email:
                demo_pwd = pysecrets.token_urlsafe(16)
                reg_ok, reg_msg = backend_register(demo_email, demo_pwd)
                login_ok, token_or_err = backend_login(demo_email, demo_pwd)
                if not login_ok:
                    st.info("Demo login failed on backend. Falling back to local demo login.")
                    ok, user_id, _ = get_or_create_user_from_email(demo_email)
                    if ok:
                        st.session_state["user_id"] = user_id
                        st.session_state["username"] = demo_email
                        st.success("Signed in with Google (local demo)!")
                        st.rerun()
                else:
                    token = token_or_err
                    st.session_state["access_token"] = token
                    ok2, me_or_err = backend_get_me(token)
                    if ok2:
                        st.session_state["user_id"] = me_or_err.get("id")
                        st.session_state["username"] = demo_email
                        st.success("Signed in with Google (backend demo)!")
                        st.rerun()
            else:
                st.info("Configure GOOGLE_DEMO_EMAIL in secrets")

    with col2:
        if st.button("Continue with GitHub", use_container_width=True, key="github_btn"):
            demo_email = st.secrets.get("GITHUB_DEMO_EMAIL", "")
            if demo_email:
                demo_pwd = pysecrets.token_urlsafe(16)
                reg_ok, reg_msg = backend_register(demo_email, demo_pwd)
                login_ok, token_or_err = backend_login(demo_email, demo_pwd)
                if not login_ok:
                    st.info("Demo login failed on backend. Falling back to local demo login.")
                    ok, user_id, _ = get_or_create_user_from_email(demo_email)
                    if ok:
                        st.session_state["user_id"] = user_id
                        st.session_state["username"] = demo_email
                        st.success("Signed in with GitHub (local demo)!")
                        st.rerun()
                else:
                    token = token_or_err
                    st.session_state["access_token"] = token
                    ok2, me_or_err = backend_get_me(token)
                    if ok2:
                        st.session_state["user_id"] = me_or_err.get("id")
                        st.session_state["username"] = demo_email
                        st.success("Signed in with GitHub (backend demo)!")
                        st.rerun()
            else:
                st.info("Configure GITHUB_DEMO_EMAIL in secrets")

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    return bool(st.session_state.get("user_id"))


def render_subject_grid(columns: int = 4) -> str | None:
    """Display subjects in a full-width card grid. Returns selected subject or None."""
    st.markdown("### 📖 Choose a Subject")
    subject_names = list(SUBJECTS.keys())
    selected = st.session_state.get("selected_subject")

    cols = st.columns(columns)
    for idx, name in enumerate(subject_names):
        info = SUBJECTS[name]
        with cols[idx % columns]:
            is_active = (name == selected)
            active_cls = " subject-selected" if is_active else ""
            st.markdown(
                f"""
                <div class='subject-card{active_cls}'>
                    <div><span class='subject-icon'>{info['icon']}</span><span class='subject-title'>{name}</span></div>
                    <div class='subject-desc'>Focused, step-by-step help tailored for {name.lower()}.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.container():
                st.markdown("<div class='subject-cta'>", unsafe_allow_html=True)
                if st.button("Start Learning", key=f"start_{name}"):
                    st.session_state["selected_subject"] = name
                    selected = name
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    return selected


def admin_ui():
    """Admin panel for viewing user data."""
    st.title("🔐 Admin Panel")
    
    # Admin password protection
    admin_pw = st.secrets.get("ADMIN_PASSWORD", None)
    if not admin_pw:
        st.error("Admin UI not configured. Set ADMIN_PASSWORD in Streamlit secrets.")
        return
    
    pw = st.text_input("Admin password", type="password")
    if not pw:
        st.info("Enter admin password to view database")
        return
    
    if pw != admin_pw:
        st.error("Wrong password")
        return
    
    # Show database connection info
    from app.db import _connect, IS_POSTGRES, DATABASE_URL
    st.subheader("🔗 Database Connection")
    
    if IS_POSTGRES:
        st.success("✅ Connected to PostgreSQL (Railway)")
        if DATABASE_URL:
            masked_url = DATABASE_URL[:20] + "..." if len(DATABASE_URL) > 20 else DATABASE_URL
            st.info(f"Database: {masked_url}")
    else:
        st.info("📁 Using local SQLite database")
    
    # Try to get real user data from the active database
    try:
        conn = _connect()
        cursor = conn.cursor()
        
        # Check which tables exist and have data
        if IS_POSTGRES:
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
            tables = [row[0] for row in cursor.fetchall()]
        else:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
        
        st.subheader("📋 Available Tables")
        st.info(f"Tables: {tables}")
        
        # Try to get users from various possible table names
        user_data = []
        for table_name in ['users', 'user']:
            if table_name in tables:
                try:
                    if IS_POSTGRES:
                        cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
                    else:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    
                    if count > 0:
                        if IS_POSTGRES:
                            cursor.execute(f'SELECT id, username, created_at FROM "{table_name}" ORDER BY id')
                        else:
                            cursor.execute(f"SELECT id, username, created_at FROM {table_name} ORDER BY id")
                        users = cursor.fetchall()
                        
                        for user in users:
                            user_data.append({
                                "id": user[0],
                                "username": user[1], 
                                "created_at": str(user[2])
                            })
                        break
                except Exception as e:
                    st.warning(f"Error reading {table_name} table: {e}")
        
        if user_data:
            st.subheader("👥 Users (Real Data)")
            st.table(user_data)
            st.success(f"Found {len(user_data)} users in database")
            
            # Download CSV
            import pandas as pd
            df = pd.DataFrame(user_data)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download users CSV", data=csv, file_name="users.csv", mime="text/csv")
        else:
            st.subheader("👥 Users")
            st.warning("No users found in any table")
            
            # Show hardcoded fallback
            st.info("Showing fallback data:")
            fallback_users = [
                {"id": 1, "username": "user1", "created_at": "2024-01-01"},
                {"id": 2, "username": "user2", "created_at": "2024-01-01"}
            ]
            st.table(fallback_users)
        
        conn.close()
        
    except Exception as e:
        st.error(f"Database error: {e}")
        st.subheader("👥 Users (Fallback)")
        st.info("Showing fallback data due to database error:")
        fallback_users = [
            {"id": 1, "username": "user1", "created_at": "2024-01-01"},
            {"id": 2, "username": "user2", "created_at": "2024-01-01"}
        ]
        st.table(fallback_users)
    
    st.subheader("🔧 Debug Info")
    st.json({
        "session_state": dict(st.session_state),
        "database_type": "PostgreSQL" if IS_POSTGRES else "SQLite",
        "database_url_set": bool(DATABASE_URL),
        "streamlit_secrets_available": hasattr(st, "secrets")
    })


