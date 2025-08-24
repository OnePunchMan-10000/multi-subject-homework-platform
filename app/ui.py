import streamlit as st
import streamlit.components.v1 as components
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

# Page CSS and styling (global theme variables and utility classes)
_GLOBAL_CSS = r"""
<style>
  /* Hide Streamlit default elements */
  #MainMenu { visibility: hidden; }
  footer { visibility: hidden; }
  header { visibility: hidden; }

  /* Theme variables */
  :root {
    --primary-100: #eef2ff;
    --primary-500: #6366f1; /* indigo */
    --primary-700: #4f46e5;
    --accent-500: #f093fb;
    --accent-600: #f5576c;
    --text-900: #0f172a;
    --muted-500: #6b7280;
    --bg-100: #ffffff;
    --card-bg: rgba(255,255,255,0.85);
    --glass-bg: rgba(255,255,255,0.08);
    --success: #10b981;
    --danger: #ef4444;
    --radius: 12px;
    --shadow-sm: 0 4px 10px rgba(15,23,42,0.06);
    --shadow-md: 0 10px 30px rgba(15,23,42,0.08);
  }

  /* Dark theme override (applied via data-theme="dark" on .stApp if desired) */
  .stApp[data-theme="dark"] {
    --text-900: #f8fafc;
    --muted-500: #94a3b8;
    --bg-100: #0b1220;
    --card-bg: rgba(8,10,14,0.6);
    --glass-bg: rgba(255,255,255,0.04);
  }

  /* Typography */
  .stApp, .stApp * { font-family: Inter, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; }
  .brand-title { font-size: 2.2rem; font-weight: 800; color: var(--text-900); }
  .brand-sub { color: var(--muted-500); margin-top: 6px; }

  /* Buttons */
  .stButton > button {
    border-radius: var(--radius);
    padding: 10px 18px;
    font-weight: 650;
    box-shadow: var(--shadow-sm);
    border: none;
  }
  .stButton > button[role="primary"] { background: linear-gradient(90deg,var(--primary-500),var(--primary-700)); color:white; }

  /* Cards */
  .card { background: var(--card-bg); border-radius: var(--radius); padding: 18px; box-shadow: var(--shadow-sm); }

  /* Glass effect */
  .glass { background: var(--glass-bg); backdrop-filter: blur(6px); border-radius: 14px; border: 1px solid rgba(255,255,255,0.06); }

  /* Hero styles */
  .hero { padding: 56px 24px; border-radius: 14px; margin-bottom: 24px; }
  .hero-title { font-size: 2.8rem; font-weight: 800; margin-bottom: 8px; }
  .hero-sub { font-size: 1.1rem; color: var(--muted-500); }

  /* Subject grid */
  .subject-grid { display:grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap: 18px; }
  .subject-card { padding: 18px; border-radius: 12px; background: var(--card-bg); transition: transform 0.22s ease, box-shadow 0.22s ease; }
  .subject-card:hover { transform: translateY(-6px); box-shadow: var(--shadow-md); }

  /* Chat */
  .chat-user { background: linear-gradient(90deg,var(--primary-500),var(--primary-700)); color: white; padding: 12px 16px; border-radius: 14px 14px 4px 14px; max-width:80%; margin-left:auto; }
  .chat-assistant { background: var(--card-bg); color: var(--text-900); padding: 12px 16px; border-radius: 14px 14px 14px 4px; max-width:80%; }

  /* Footer */
  .app-footer { padding: 28px 12px; text-align:center; color:var(--muted-500); }

  /* Utilities */
  .muted { color: var(--muted-500); }
  .mb-12 { margin-bottom: 12px; }
  .mb-24 { margin-bottom: 24px; }

  @media (max-width: 768px) {
    .hero-title { font-size: 2rem; }
  }

</style>
"""

def render_global_css():
    """Inject global CSS into the page. This is presentational only."""
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)


def render_navigation():
    """Render the top navigation menu"""
    # Navigation intentionally disabled for a minimal layout.
    return


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


def render_landing_page():
    """Render a modern landing page with gold/black theme, feature cards, and new branding"""
    # Gold/black gradient with geometric shapes
    st.markdown("""
    <style>
        .landing-bg {
            background: linear-gradient(135deg, #000000 0%, #d4af37 100%);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            min-height: 100vh;
            padding: 4rem 2rem;
        }
        @keyframes gradient {
            0% {background-position: 0% 50%;}
            50% {background-position: 100% 50%;}
            100% {background-position: 0% 50%;}
        }
        .hero-title {
            font-size: 3.5rem;
            font-weight: 800;
            color: white;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .hero-sub {
            color: white;
            opacity: 0.9;
            font-size: 1.2rem;
            margin-top: 1rem;
        }
        .feature-card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .feature-card:hover {
            transform: translateY(-5px);
        }
    
    </style>
    """, unsafe_allow_html=True)

    # Render hero and feature cards using a raw HTML component to avoid markdown escaping
    html_content = """
<style>
  .landing-inner { max-width:1000px; margin:0 auto; padding:48px 24px; text-align:center; }
  .landing-hero { padding: 48px; border-radius: 12px; background: linear-gradient(135deg,#a67c00,#d4af37); color: #fff; }
  .landing-hero h1 { margin: 0; font-size:48px; letter-spacing:2px; }
  .landing-hero p { margin: 12px 0; opacity:0.95; }
  .feature-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:16px; margin-top:24px; }
  .feature-card { background: rgba(0,0,0,0.12); padding:18px; border-radius:12px; color:#fff; }
</style>

<div class='landing-inner'>
  <div class='landing-hero'>
    <div style='font-size:48px;'>👑</div>
    <h1>EDULLM</h1>
    <p style='font-weight:600; margin-top:8px;'>Your AI-Powered Study Companion</p>
    <p style='max-width:720px; margin:12px auto 0;'>Get instant, step-by-step homework solutions with personalized explanations from advanced AI.</p>
  </div>

  <div class='feature-grid'>
    <div class='feature-card'>
      <h3>Smart AI Tutor</h3>
      <p>Adapts explanations to your unique learning style</p>
    </div>
    <div class='feature-card'>
      <h3>Step-by-Step Solutions</h3>
      <p>Breaks down problems into clear, logical steps</p>
    </div>
    <div class='feature-card'>
      <h3>Progress Tracking</h3>
      <p>Tracks your learning journey with detailed history</p>
    </div>
  </div>

  <div style='margin-top:28px; text-align:center;'>
    <!-- Streamlit button placed below for functionality -->
  </div>

  <div style='text-align:center; color:rgba(255,255,255,0.75); margin-top:32px;'>© 2025 by Praveen</div>
</div>
"""

    try:
        components.html(html_content, height=520)
    except Exception:
        # Fallback: render as simple markdown header
        st.header('Edullm')
        st.write('Your virtual study companion — clear, step-by-step homework solutions.')

    # Functional Streamlit button to trigger login flow
    if st.button('Start Learning', key='landing_start'):
        st.session_state['show_login'] = True
        st.rerun()

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


def auth_ui():
    """Render the authentication UI using Streamlit form and call backend_login/backend_get_me.

    This replaces the previous purely-HTML UI so the Sign In button works and updates
    Streamlit session state with `access_token`, `user_id`, and `username`.
    """
    st.markdown("""
    <style>
      .auth-container { max-width: 900px; margin: 40px auto; padding: 28px; border-radius: 12px; background: rgba(255,255,255,0.04); }
      .auth-title { font-size: 2rem; margin-bottom: 12px; }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        st.markdown("<div class='auth-title'><strong>Welcome back!</strong> ✨</div>", unsafe_allow_html=True)

        # Use a proper Streamlit form so values are available to Python
        with st.form(key='login_form'):
            username = st.text_input('Email or username', value='')
            password = st.text_input('Password', type='password')
            submit = st.form_submit_button('Sign In')

        if submit:
            # Call backend to authenticate
            with st.spinner('Signing in...'):
                ok, token_or_msg = backend_login(username, password)
                if not ok:
                    st.error(f"Login failed: {token_or_msg}")
                else:
                    # Store access token and fetch user profile
                    st.session_state['access_token'] = token_or_msg
                    ok2, me_or_msg = backend_get_me(token_or_msg)
                    if ok2 and isinstance(me_or_msg, dict):
                        st.session_state['user_id'] = me_or_msg.get('id') or me_or_msg.get('username')
                        st.session_state['username'] = me_or_msg.get('username', '')
                    else:
                        # If profile fetch fails, still allow login but warn
                        st.warning(f"Signed in but couldn't fetch profile: {me_or_msg}")
                    # Hide login view and rerun
                    st.session_state['show_login'] = False
                    st.experimental_rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    return True


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


def inject_global_css():
    st.markdown("""
    <style>
        :root {
            --gold: #f1c40f;
            --gray: #6b7280;
        }
        .top-right-btn {
            position: fixed;
            top: 1rem;
            right: 1rem;
            border: 1px solid #e5e7eb;
            border-radius: 0.375rem;
            padding: 0.5rem 1rem;
            background: white;
            z-index: 100;
        }
        .hero {
            text-align: center;
            margin-top: 4rem;
            padding: 2rem;
        }
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.5rem;
            margin: 3rem auto;
            max-width: 1200px;
        }
        .feature-card {
            padding: 1.5rem;
            border-radius: 0.5rem;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .cta-button {
            padding: 0.75rem 1.5rem;
            border-radius: 0.375rem;
            font-weight: 600;
            margin: 0.5rem;
        }
    </style>
    """, unsafe_allow_html=True)


def render_login_button():
    st.markdown("""
    <a href='/login' class='top-right-btn'>
        <span class='mr-2'>🔐</span> Login
    </a>
    """, unsafe_allow_html=True)


def render_hero():
    st.markdown("""
    <div class='hero'>
        <h1 style='color: var(--gold); font-size: 3rem; font-weight: 800; margin-bottom: 1rem'>EduLLM</h1>
        <p style='color: var(--gray); font-size: 1.1rem; max-width: 600px; margin: 0 auto'>
            Your AI-powered homework companion. Get instant, accurate answers to your school questions using cutting-edge Large Language Model technology.
        </p>
        <div style='display: flex; justify-content: center; gap: 1rem; margin-top: 1.5rem'>
            <button class='cta-button' style='background: var(--gold); color: black'>Start Learning</button>
            <button class='cta-button' style='border: 1px solid #e5e7eb'>Learn More</button>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_features():
    st.markdown("""
    <div style='padding: 2rem 1rem'>
        <h2 style='text-align: center; font-size: 1.75rem; margin-bottom: 2rem'>
            Why Choose <span style='color: var(--gold)'>EduLLM</span>?
        </h2>
        <div class='feature-grid'>
            <div class='feature-card'>
                <p style='font-size: 2rem; margin: 0'>🧠</p>
                <h3 style='margin: 0.5rem 0'>AI-Powered Learning</h3>
                <p style='color: var(--gray); margin: 0'>Advanced LLM technology helps you understand complex concepts.</p>
            </div>
            <div class='feature-card'>
                <p style='font-size: 2rem; margin: 0'>📘</p>
                <h3 style='margin: 0.5rem 0'>Multiple Subjects</h3>
                <p style='color: var(--gray); margin: 0'>Math, Science, History, English and more.</p>
            </div>
            <div class='feature-card'>
                <p style='font-size: 2rem; margin: 0'>💡</p>
                <h3 style='margin: 0.5rem 0'>Instant Solutions</h3>
                <p style='color: var(--gray); margin: 0'>Step-by-step solutions in seconds.</p>
            </div>
            <div class='feature-card'>
                <p style='font-size: 2rem; margin: 0'>👥</p>
                <h3 style='margin: 0.5rem 0'>Student Community</h3>
                <p style='color: var(--gray); margin: 0'>Join thousands improving their grades.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


