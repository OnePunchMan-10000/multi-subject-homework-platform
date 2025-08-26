import streamlit as st
import time
import streamlit.components.v1 as components
import re
import html
import secrets as pysecrets
from app.subjects import SUBJECTS
from app.backend import backend_register, backend_login, backend_get_me
from app.backend import backend_save_history
from app.db import get_or_create_user_from_email, authenticate_user, register_user
import os
import subprocess
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
    """Removed - using pure Streamlit components instead of custom CSS."""
    pass


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
    """Render the homepage with subject selection and question interface"""
    from app.llm import get_api_response
    from app.formatting import format_response
    from app.visualization import should_show_diagram, create_smart_visualization
    from app.backend import backend_save_history, backend_get_history
    from app.db import save_history, load_history
    
    # Check current page (only after login)
    current_page = st.session_state.get('current_page', 'home')
    
    # Handle different pages
    if current_page == 'profile':
        render_profile_page()
        render_footer()
        return
    elif current_page == 'about':
        render_about_page()
        render_footer()
        return
    elif current_page == 'admin':
        admin_ui()
        render_footer()
        return
    elif current_page == 'subjects':
        # Set selected_subject to None to show subject grid
        st.session_state["selected_subject"] = None

    # Stage 1: Subject-only page - clean and simple
    if not st.session_state.get("selected_subject"):
        _ = render_subject_grid(columns=4)
        return

    # Stage 2: Question UI after subject selection
    selected_subject = st.session_state.get("selected_subject")
    
    # Header using pure Streamlit
    st.markdown(f"# ❓ {selected_subject} Question")
    st.markdown("**Ask your question and get a detailed step-by-step solution**")
    
    # Change subject button
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("← Back to Subjects", use_container_width=True):
            st.session_state["selected_subject"] = None
            st.rerun()
    
    st.markdown("---")

    # Question input
    question = st.text_area(
        f"📝 Enter your {selected_subject} question:",
        height=150,
        placeholder=f"Example: Solve the equation 2x + 5 = 13, or explain photosynthesis...",
        help="Be specific and include all relevant details for the best solution"
    )
    
    if st.button("🎯 Get Solution", type="primary"):
        if question.strip():
            with st.spinner("Getting solution..."):
                response = get_api_response(question, selected_subject)
                
                if response:
                    st.markdown("---")
                    st.markdown(f"## 📚 {selected_subject} Solution")
                    
                    # Display solution in a clean container
                    formatted_response = format_response(response)
                    with st.container():
                        st.markdown(formatted_response, unsafe_allow_html=True)
                    # Save to history (backend)
                    if backend_save_history(selected_subject, question.strip(), formatted_response):
                        pass  # Successfully saved
                    else:
                        # Fallback to local save if backend fails
                        save_history(
                            st.session_state["user_id"],
                            selected_subject,
                            question.strip(),
                            formatted_response,
                        )
                    
                    # Show diagram if needed
                    if should_show_diagram(question, selected_subject):
                        st.markdown("### 📊 Visualization")
                        viz = create_smart_visualization(question, selected_subject)
                        if viz:
                            # Display visualization at a controlled width so it doesn't stretch full container
                            st.image(viz, width=700)
                    
                    # Simple feedback
                    st.markdown("### Rate this solution")
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button("👍 Helpful"):
                            st.success("Thanks!")
                    with col_b:
                        if st.button("👎 Needs work"):
                            st.info("We'll improve!")
                    with col_c:
                        if st.button("🔄 Try again"):
                            st.rerun()
        else:
            st.warning("Please enter a question.")
    
    # History + footer
    with st.expander("🕘 View your recent history"):
        # Try to load from backend first, fallback to local
        rows = backend_get_history(limit=25)
        if not rows:
            rows = load_history(st.session_state["user_id"], limit=25)
        if not rows:
            st.info("No history yet.")
        else:
            for row in rows:
                # Handle both backend format (dict) and local format (tuple)
                if isinstance(row, dict):
                    subj, q, created_at = row['subject'], row['question'], row['created_at']
                else:
                    _id, subj, q, a, created_at = row
                    
                st.markdown(f"**[{created_at}] {subj}**")
                st.markdown(f"- Question: {q}")
                # Intentionally do not render the answer to reduce visual bloat and storage usage in UI
                st.markdown("---")


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
    """Clean login page using pure Streamlit components."""
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Title and subtitle
        st.markdown("# 🔐 Sign In")
        st.markdown("**Welcome back! Please sign in to continue.**")
        
        st.markdown("---")

        # Login form
        with st.form(key='login_form'):
            st.text_input('Username', key='login_username', placeholder='Enter your username')
            st.text_input('Password', type='password', key='login_password', placeholder='Enter your password')
            login_submit = st.form_submit_button('🚀 Login', type='primary', use_container_width=True)

        if login_submit:
            username = st.session_state.get('login_username', '')
            password = st.session_state.get('login_password', '')
            
            if not username or not password:
                st.error('Please enter both username and password')
            else:
                # Use backend login like hw01.py does (this works!)
                from app.backend import backend_login, backend_get_me
                
                ok, token_or_err = backend_login(username, password)
                if ok:
                    token = token_or_err
                    st.session_state["access_token"] = token
                    
                    # Get user info like hw01.py does
                    ok2, me_or_err = backend_get_me(token)
                    if ok2:
                        st.session_state["user_id"] = me_or_err.get("id")
                        st.session_state["username"] = me_or_err.get("username")
                        st.session_state['show_login'] = False
                        st.session_state['current_page'] = 'home'  # This will show subjects
                        st.session_state['selected_subject'] = None  # Start at subjects page
                        
                        st.success(f'✅ Welcome back, {username}!')
                        st.rerun()
                        return True
                    else:
                        st.error(f"Login succeeded but fetching user failed: {me_or_err}")
                else:
                    st.error(f'Login failed: {token_or_err}')

        st.markdown("---")
        
        # Back to landing page option
        if st.button('← Back to Home', use_container_width=True):
            st.session_state['show_login'] = False
            st.rerun()

    return False


def render_subject_grid(columns: int = 4) -> str | None:
    """Display subjects using pure Streamlit components."""
    
    # Header
    st.markdown("# 📚 Choose Your Subject")
    st.markdown("**Select a subject to get started with your homework questions**")
    st.markdown("---")
    
    subject_names = list(SUBJECTS.keys())
    selected = st.session_state.get("selected_subject")

    # Create subject grid using columns
    cols = st.columns(columns)
    for idx, name in enumerate(subject_names):
        info = SUBJECTS[name]
        with cols[idx % columns]:
            # Subject card using native Streamlit components
            st.markdown(f"### {info['icon']} {name}")
            st.markdown(f"Get step-by-step solutions for {name.lower()} problems")
            
            if st.button(f"Select {name}", key=f"select_{name}", use_container_width=True, type="primary"):
                st.session_state["selected_subject"] = name
                selected = name
                st.rerun()
            
            st.markdown("")  # Add space between cards

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


def get_deploy_commit_sha() -> str:
    """Return the current git commit SHA if available; return 'unknown' otherwise.

    This reads from the local git HEAD; on the deployed environment it may be present.
    """
    try:
        # Try environment variable first (some hosts expose it)
        sha = os.environ.get('DEPLOY_COMMIT')
        if sha:
            return sha[:10]
        # Fallback to local git
        out = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.DEVNULL).decode().strip()
        return out[:10]
    except Exception:
        return 'unknown'


def render_login_button():
    st.markdown("""
    <a href='/login' class='top-right-btn'>
        <span class='mr-2'>🔐</span> Login
    </a>
    """, unsafe_allow_html=True)


def render_hero():
    """Hero removed per request; landing page is minimal and functional via render_landing_page()."""
    return


def render_features():
    """Features section removed per request. Use minimal landing page only."""
    return


def render_landing_page():
    """Landing page matching your exact design - with crown logo and golden theme."""
    
    # Custom CSS for the exact design you showed me
    st.markdown("""
    <style>
    .landing-hero {
        text-align: center;
        padding: 3rem 1rem;
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border-radius: 20px;
        margin-bottom: 2rem;
    }
    
    .crown-logo {
        position: relative;
        display: inline-block;
        margin-bottom: 2rem;
    }
    
    .crown-icon {
        font-size: 3rem;
        position: absolute;
        top: -20px;
        left: 50%;
        transform: translateX(-50%);
    }
    
    .brand-letter {
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, #F4C430, #FFA500);
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        font-weight: 800;
        color: white;
        margin: 0 auto;
        box-shadow: 0 8px 32px rgba(244, 196, 48, 0.3);
    }
    
    .landing-title {
        font-size: 4rem;
        font-weight: 800;
        color: #F4C430;
        margin: 2rem 0 1rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .landing-subtitle {
        font-size: 1.2rem;
        color: #6b7280;
        max-width: 600px;
        margin: 0 auto 3rem auto;
        line-height: 1.6;
    }
    
    .features-section {
        background: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 2rem 0;
    }
    
    .section-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .text-gold {
        color: #F4C430;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 2rem;
        margin-top: 2rem;
    }
    
    .feature-card {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid #e9ecef;
    }
    
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.12);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }
    
    .feature-title {
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #1f2937;
    }
    
    .feature-desc {
        color: #6b7280;
        line-height: 1.5;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero section with crown logo (exactly like your design)
    st.markdown("""
    <div class="landing-hero">
        <div class="crown-logo">
            <div class="crown-icon">👑</div>
            <div class="brand-letter">E</div>
        </div>
        
        <h1 class="landing-title">EduLLM</h1>
        
        <p class="landing-subtitle">
            Your AI-powered homework companion. Get instant, accurate answers
            to your school questions using cutting-edge Large Language Model
            technology.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Buttons (working with Streamlit backend)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button('🚀 Start Learning', type='primary', use_container_width=True):
            st.session_state['show_login'] = True
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button('📖 Learn More', use_container_width=True):
            st.info("Scroll down to see all features!")
    
    # Features section (exactly like your design)
    st.markdown("""
    <div class="features-section">
        <h2 class="section-title">Why Choose <span class="text-gold">EduLLM?</span></h2>
        
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">🧠</div>
                <h3 class="feature-title">AI-Powered Learning</h3>
                <p class="feature-desc">Advanced LLM technology helps you understand complex concepts with personalized explanations.</p>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">📖</div>
                <h3 class="feature-title">Multiple Subjects</h3>
                <p class="feature-desc">Get help with Math, Science, History, English, and more - all in one platform.</p>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">💡</div>
                <h3 class="feature-title">Instant Solutions</h3>
                <p class="feature-desc">Get step-by-step solutions to your homework problems in seconds.</p>
            </div>
            
            <div class="feature-card">
                <div class="feature-icon">👥</div>
                <h3 class="feature-title">Student Community</h3>
                <p class="feature-desc">Join thousands of students who are already improving their grades with EduLLM.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Final CTA
    st.markdown("### 🎯 Ready to Ace Your Homework?")
    st.markdown("Join thousands of students who are already using EduLLM to improve their understanding and grades.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button('🎯 Get Started Today', type='primary', use_container_width=True):
            st.session_state['show_login'] = True
            st.rerun()


