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
    st.markdown(f"""
    <style>
    /* Hide streamlit elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stDeployButton {{visibility: hidden;}}
    
    .stApp {{
        background-image: url('{login_bg_url}') !important;
        background-size: cover !important; 
        background-position: center !important; 
        background-attachment: fixed !important;
    }}
    
    .auth-container {{
        background: rgba(45, 55, 75, 0.95);
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 20px 40px rgba(0,0,0,0.6);
        backdrop-filter: blur(20px);
        max-width: 480px;
        margin: 5vh auto;
        padding: 3rem 2.5rem;
        color: white;
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
    """Admin-only DB viewer (requires ADMIN_PASSWORD in st.secrets)."""
    admin_pw = st.secrets.get("ADMIN_PASSWORD", None)
    if not admin_pw:
        st.error("Admin UI not configured. Set ADMIN_PASSWORD in Streamlit secrets.")
        return

    pw = st.text_input("Admin password", type="password")
    if not pw:
        st.info("Enter admin password to view DB")
        return

    if pw != admin_pw:
        st.error("Wrong password")
        return

    # Debug: Show current session state
    st.subheader("🔍 Debug: Session State")
    st.json(st.session_state)
    
    # Use the SAME database connection method as the main app
    try:
        # Import the database module to use the same connection logic
        from app.db import _connect
        
        st.subheader("🔗 Database Connection")
        st.info("Using the same database connection method as the main app...")
        
        # Get database connection using the app's method
        conn = _connect()
        if not conn:
            st.error("❌ Failed to get database connection using app's method")
            return
            
        st.success("✅ Connected to database using app's connection method")
        
        # Check if tables exist
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        st.info(f"📋 Available tables: {[t[0] for t in tables]}")
        
        # Show users with detailed debugging
        if ('users',) in tables:
            st.subheader("👥 Users")
            
            # Check table structure
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            st.info(f"Users table columns: {[col[1] for col in columns]}")
            
            # Check row count
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            st.info(f"Total users in table: {user_count}")
            
            if user_count > 0:
                df_users = pd.read_sql_query("SELECT id, username, created_at FROM users ORDER BY id DESC", conn)
                st.table(df_users)
                st.success(f"Found {len(df_users)} users")
                
                # Show raw data for verification
                cursor.execute("SELECT * FROM users ORDER BY id DESC")
                raw_users = cursor.fetchall()
                st.info(f"Raw user data: {raw_users}")
            else:
                st.warning("Users table exists but is empty")
                
                # Try to see if there are any rows at all
                cursor.execute("SELECT * FROM users LIMIT 5")
                any_rows = cursor.fetchall()
                if any_rows:
                    st.info(f"Raw user data found: {any_rows}")
                else:
                    st.info("No user rows found in table")
        else:
            st.warning("Users table not found")

        # Show history with detailed debugging
        if ('history',) in tables:
            st.subheader("📝 Recent History")
            
            # Check table structure
            cursor.execute("PRAGMA table_info(history)")
            columns = cursor.fetchall()
            st.info(f"History table columns: {[col[1] for col in columns]}")
            
            # Check row count
            cursor.execute("SELECT COUNT(*) FROM history")
            history_count = cursor.fetchone()[0]
            st.info(f"Total history entries: {history_count}")
            
            if history_count > 0:
                df_hist = pd.read_sql_query("""
                    SELECT h.id, u.username, h.subject, substr(h.question,1,200) as question_preview, h.created_at
                    FROM history h JOIN users u ON h.user_id = u.id
                    ORDER BY h.id DESC LIMIT 50
                """, conn)
                st.table(df_hist)
                st.success(f"Found {len(df_hist)} history entries")
                
                # Show raw data for verification
                cursor.execute("SELECT * FROM history ORDER BY id DESC LIMIT 10")
                raw_history = cursor.fetchall()
                st.info(f"Raw history data: {raw_history}")
            else:
                st.warning("History table exists but is empty")
                
                # Try to see if there are any rows at all
                cursor.execute("SELECT * FROM history LIMIT 5")
                any_rows = cursor.fetchall()
                if any_rows:
                    st.info(f"Raw history data found: {any_rows}")
                else:
                    st.info("No history rows found in table")
        else:
            st.warning("History table not found")

        # Try direct queries without JOIN to see if data exists
        st.subheader("🔍 Direct Table Queries (Debug)")
        
        if ('users',) in tables:
            cursor.execute("SELECT * FROM users")
            all_users = cursor.fetchall()
            st.info(f"All users (raw): {all_users}")
        
        if ('history',) in tables:
            cursor.execute("SELECT * FROM history")
            all_history = cursor.fetchall()
            st.info(f"All history (raw): {all_history}")

        # Download users CSV if users exist
        if ('users',) in tables and user_count > 0:
            df_users = pd.read_sql_query("SELECT id, username, created_at FROM users ORDER BY id DESC", conn)
            csv = df_users.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download users CSV", data=csv, file_name="users.csv", mime="text/csv")

        conn.close()
        
    except ImportError:
        st.error("❌ Could not import app.db module. Using fallback connection method...")
        
        # Fallback: Try to find database file
        possible_paths = [
            "app_data.db",  # Current directory
            "/tmp/app_data.db",  # Temp directory
            "/home/appuser/app_data.db",  # User home
            os.path.join(os.getcwd(), "app_data.db"),  # Full path
            os.path.join(os.path.dirname(__file__), "..", "app_data.db"),  # Relative to app folder
        ]
        
        db_path = None
        for path in possible_paths:
            if os.path.exists(path):
                db_path = path
                break
        
        if not db_path:
            st.error("❌ Database not found! Tried these paths:")
            for path in possible_paths:
                st.write(f"   • {path}")
            st.warning("The database might be in a different location on Streamlit Sharing.")
            return

        st.success(f"✅ Database found at: {db_path}")
        st.info(f"📁 File size: {os.path.getsize(db_path)} bytes")
        
        try:
            conn = sqlite3.connect(db_path)
            
            # Check if tables exist
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            st.info(f"📋 Available tables: {[t[0] for t in tables]}")
            
            # Show users with detailed debugging
            if ('users',) in tables:
                st.subheader("👥 Users")
                
                # Check table structure
                cursor.execute("PRAGMA table_info(users)")
                columns = cursor.fetchall()
                st.info(f"Users table columns: {[col[1] for col in columns]}")
                
                # Check row count
                cursor.execute("SELECT COUNT(*) FROM users")
                user_count = cursor.fetchone()[0]
                st.info(f"Total users in table: {user_count}")
                
                if user_count > 0:
                    df_users = pd.read_sql_query("SELECT id, username, created_at FROM users ORDER BY id DESC", conn)
                    st.table(df_users)
                    st.success(f"Found {len(df_users)} users")
                else:
                    st.warning("Users table exists but is empty")
                    
                    # Try to see if there are any rows at all
                    cursor.execute("SELECT * FROM users LIMIT 5")
                    any_rows = cursor.fetchall()
                    if any_rows:
                        st.info(f"Raw user data found: {any_rows}")
                    else:
                        st.info("No user rows found in table")
            else:
                st.warning("Users table not found")

            # Show history with detailed debugging
            if ('history',) in tables:
                st.subheader("📝 Recent History")
                
                # Check table structure
                cursor.execute("PRAGMA table_info(history)")
                columns = cursor.fetchall()
                st.info(f"History table columns: {[col[1] for col in columns]}")
                
                # Check row count
                cursor.execute("SELECT COUNT(*) FROM history")
                history_count = cursor.fetchone()[0]
                st.info(f"Total history entries: {history_count}")
                
                if history_count > 0:
                    df_hist = pd.read_sql_query("""
                        SELECT h.id, u.username, h.subject, substr(h.question,1,200) as question_preview, h.created_at
                        FROM history h JOIN users u ON h.user_id = u.id
                        ORDER BY h.id DESC LIMIT 50
                    """, conn)
                    st.table(df_hist)
                    st.success(f"Found {len(df_hist)} history entries")
                else:
                    st.warning("History table exists but is empty")
                    
                    # Try to see if there are any rows at all
                    cursor.execute("SELECT * FROM history LIMIT 5")
                    any_rows = cursor.fetchall()
                    if any_rows:
                        st.info(f"Raw history data found: {any_rows}")
                    else:
                        st.info("No history rows found in table")
            else:
                st.warning("History table not found")

            # Try direct queries without JOIN to see if data exists
            st.subheader("🔍 Direct Table Queries (Debug)")
            
            if ('users',) in tables:
                cursor.execute("SELECT * FROM users")
                all_users = cursor.fetchall()
                st.info(f"All users (raw): {all_users}")
            
            if ('history',) in tables:
                cursor.execute("SELECT * FROM history")
                all_history = cursor.fetchall()
                st.info(f"All history (raw): {all_history}")

            # Download users CSV if users exist
            if ('users',) in tables and user_count > 0:
                df_users = pd.read_sql_query("SELECT id, username, created_at FROM users ORDER BY id DESC", conn)
                csv = df_users.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Download users CSV", data=csv, file_name="users.csv", mime="text/csv")

            conn.close()
            
        except Exception as e:
            st.error(f"❌ Database error: {e}")
            st.error("This might be a database connection or permission issue on Streamlit Sharing.")
            import traceback
            st.error(f"Full error traceback: {traceback.format_exc()}")
            
    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.error("This might be a database connection or permission issue on Streamlit Sharing.")
        import traceback
        st.error(f"Full error traceback: {traceback.format_exc()}")


