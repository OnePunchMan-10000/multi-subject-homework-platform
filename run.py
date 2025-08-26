"""EduLLM - Complete AI Study Assistant with Professional UI"""

import streamlit as st
import requests
import json
import os
import hashlib

# Set page config with crown branding
st.set_page_config(
    page_title="👑 EduLLM - AI Study Assistant",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'landing'
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'selected_subject' not in st.session_state:
    st.session_state.selected_subject = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'auth_tab' not in st.session_state:
    st.session_state.auth_tab = 'login'
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Professional CSS Styling
def load_css():
    # Get theme colors - Study-themed with gold/silver/black
    if st.session_state.dark_mode:
        bg_color = """
            radial-gradient(circle at 20% 80%, rgba(255, 215, 0, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(192, 192, 192, 0.1) 0%, transparent 50%),
            linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 25%, #2d2d2d 50%, #1a1a1a 75%, #0f0f0f 100%)
        """
        text_color = "#ffffff"
        card_bg = "rgba(30, 30, 30, 0.95)"
        subtitle_color = "#c0c0c0"
    else:
        bg_color = """
            radial-gradient(circle at 20% 80%, rgba(255, 215, 0, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(192, 192, 192, 0.15) 0%, transparent 50%),
            linear-gradient(135deg, #fafafa 0%, #f0f0f0 25%, #ffffff 50%, #f0f0f0 75%, #fafafa 100%)
        """
        text_color = "#333333"
        card_bg = "rgba(255, 255, 255, 0.95)"
        subtitle_color = "#666666"

    st.markdown(f"""
    <style>
    /* Hide Streamlit default elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stDeployButton {{visibility: hidden;}}

    /* Global Background with Study Theme */
    .stApp {{
        background: {bg_color};
        color: {text_color};
        position: relative;
    }}

    /* Study-themed decorative elements */
    .stApp::before {{
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image:
            radial-gradient(circle at 10% 20%, rgba(255, 215, 0, 0.05) 0%, transparent 20%),
            radial-gradient(circle at 90% 80%, rgba(192, 192, 192, 0.05) 0%, transparent 20%);
        pointer-events: none;
        z-index: -1;
    }}

    /* Dark Mode Toggle */
    .theme-toggle {{
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        border: none;
        border-radius: 50px;
        padding: 10px 20px;
        color: white;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
        transition: all 0.3s ease;
    }}

    .theme-toggle:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
    }}

    /* Landing Page Styles */
    .landing-container {{
        text-align: center;
        padding: 2rem 1rem;
        max-width: 1200px;
        margin: 0 auto;
        min-height: 80vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }}

    .crown-logo {{
        position: relative;
        display: inline-block;
        margin-bottom: 2rem;
    }}

    .crown-icon {{
        font-size: 2.5rem;
        position: absolute;
        top: -15px;
        left: 50%;
        transform: translateX(-50%);
        color: #FFD700;
    }}

    .brand-letter {{
        width: 100px;
        height: 100px;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3.5rem;
        font-weight: 900;
        color: white;
        margin: 0 auto;
        box-shadow: 0 10px 40px rgba(255, 215, 0, 0.3);
        border: 3px solid rgba(255, 255, 255, 0.2);
    }}

    .landing-title {{
        font-size: 3.5rem;
        font-weight: 800;
        color: #FFD700;
        margin: 2rem 0 1rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}

    .landing-subtitle {{
        font-size: 1.3rem;
        color: {subtitle_color};
        max-width: 600px;
        margin: 0 auto 2rem auto;
        line-height: 1.6;
        text-align: center;
        display: block;
        width: 100%;
    }}

    /* Flash Cards - Single Row Layout */
    .flash-cards {{
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 4rem 0;
        flex-wrap: wrap;
        max-width: 1200px;
        margin-left: auto;
        margin-right: auto;
    }}

    .flash-card {{
        background: {card_bg};
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 1px solid rgba(255, 215, 0, 0.2);
        transition: all 0.3s ease;
        flex: 1;
        min-width: 250px;
        max-width: 280px;
        backdrop-filter: blur(10px);
    }}

    .flash-card:hover {{
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(255, 215, 0, 0.2);
        border-color: #FFD700;
    }}

    .flash-card-icon {{
        font-size: 3rem;
        margin-bottom: 1rem;
        color: #FFD700;
    }}

    .flash-card-title {{
        font-size: 1.3rem;
        font-weight: 600;
        color: {text_color};
        margin-bottom: 0.8rem;
    }}

    .flash-card-desc {{
        color: {subtitle_color};
        font-size: 0.95rem;
        line-height: 1.5;
    }}

    /* Navigation Bar */
    .navbar {{
        background: linear-gradient(135deg, #FFD700, #FFA500);
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        position: sticky;
        top: 0;
        z-index: 1000;
        margin-bottom: 2rem;
    }}

    .navbar-brand {{
        display: flex;
        align-items: center;
        font-size: 1.5rem;
        font-weight: 700;
        color: white;
        text-decoration: none;
    }}

    .navbar-nav {{
        display: flex;
        gap: 2rem;
        align-items: center;
    }}

    .nav-link {{
        color: white;
        text-decoration: none;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        transition: background 0.3s ease;
        cursor: pointer;
    }}

    .nav-link:hover {{
        background: rgba(255,255,255,0.2);
    }}

    .nav-link.active {{
        background: rgba(255,255,255,0.3);
    }}

    /* Centered Auth Container */
    .auth-container {{
        max-width: 450px;
        margin: 2rem auto;
        background: {card_bg};
        border-radius: 20px;
        box-shadow: 0 15px 50px rgba(0,0,0,0.15);
        overflow: hidden;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 215, 0, 0.2);
    }}

    .auth-tabs {{
        display: flex;
        background: rgba(248, 249, 250, 0.1);
    }}

    .auth-tab {{
        flex: 1;
        padding: 1rem;
        text-align: center;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        background: transparent;
        color: {text_color};
    }}

    .auth-tab.active {{
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: white;
    }}

    .auth-form {{
        padding: 2.5rem;
    }}

    /* Center login page */
    .login-page {{
        min-height: 90vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 1rem;
        margin-top: -2rem;
    }}

    .login-header {{
        text-align: center;
        margin-bottom: 2rem;
    }}

    .login-form-container {{
        width: 100%;
        max-width: 450px;
        margin: 0 auto;
    }}
    </style>
    """, unsafe_allow_html=True)

# Subject definitions
SUBJECTS = {
    "Mathematics": {
        "icon": "📐",
        "desc": "Algebra, Calculus, Geometry, Statistics",
        "prompt": "You are an expert mathematics tutor. Provide clear, step-by-step solutions with proper explanations."
    },
    "Physics": {
        "icon": "⚡",
        "desc": "Mechanics, Thermodynamics, Electromagnetism",
        "prompt": "You are a senior physics tutor. Provide clear, step-by-step solutions with proper units and explanations."
    },
    "Chemistry": {
        "icon": "⚗️",
        "desc": "Organic, Inorganic, Physical Chemistry",
        "prompt": "You are a chemistry expert. Provide detailed, educational solutions with proper chemical notation."
    },
    "Biology": {
        "icon": "🧬",
        "desc": "Cell Biology, Genetics, Ecology",
        "prompt": "You are a biology tutor. Provide comprehensive explanations with relevant examples."
    },
    "English": {
        "icon": "📖",
        "desc": "Literature, Grammar, Writing",
        "prompt": "You are an English expert. Provide detailed analysis with examples and proper explanations."
    },
    "History": {
        "icon": "📜",
        "desc": "World History, Analysis, Research",
        "prompt": "You are a history expert. Provide comprehensive analysis with context and significance."
    },
    "Economics": {
        "icon": "📊",
        "desc": "Micro, Macro, Econometrics",
        "prompt": "You are an economics expert. Provide clear analysis with real-world examples."
    },
    "Geography": {
        "icon": "🌍",
        "desc": "Physical, Human, Environmental",
        "prompt": "You are a geography expert. Provide comprehensive analysis with spatial relationships."
    },
    "Computer Science": {
        "icon": "💻",
        "desc": "Programming, Algorithms, Data Structures",
        "prompt": "You are a computer science expert. Provide detailed solutions with code examples when relevant."
    }
}

# API Functions
def get_api_response(question, subject):
    """Get response from OpenRouter API"""
    if 'OPENROUTER_API_KEY' not in st.secrets:
        st.error("⚠️ API key not configured. Please add OPENROUTER_API_KEY to Streamlit secrets.")
        return None

    api_key = st.secrets['OPENROUTER_API_KEY']

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    model = "openai/gpt-4o-mini"
    if subject in ("Physics", "Chemistry"):
        model = "openai/gpt-4o"

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": SUBJECTS[subject]['prompt']},
            {"role": "user", "content": question}
        ],
        "temperature": 0.1,
        "max_tokens": 2000
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=body,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            st.error("Service temporarily unavailable. Please try again.")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Network Error: {str(e)}")
        return None

def format_response(response):
    """Format the AI response for better display"""
    if not response:
        return ""

    lines = response.split('\n')
    formatted_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            formatted_lines.append('')
            continue

        if line.startswith('#'):
            formatted_lines.append(f"**{line.replace('#', '').strip()}**")
        elif line.startswith('Step') or line.startswith('Solution'):
            formatted_lines.append(f"**{line}**")
        else:
            formatted_lines.append(line)

    return '\n\n'.join(formatted_lines)

# Theme Toggle Component
def render_theme_toggle():
    """Render theme toggle button"""
    col1, col2, col3 = st.columns([8, 1, 1])
    with col3:
        theme_icon = "🌙" if st.session_state.dark_mode else "☀️"
        if st.button(f"{theme_icon}", key="theme_toggle", help="Toggle Dark/Light Mode"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

# Page Components
def render_navbar():
    """Render the navigation bar"""
    st.markdown("""
    <div class="navbar">
        <div class="navbar-brand">
            <span style="margin-right: 10px;">👑</span>
            EduLLM
        </div>
        <div class="navbar-nav">
            <span class="nav-link active">Home</span>
            <span class="nav-link">Subjects</span>
            <span class="nav-link">About</span>
            <span class="nav-link">Profile</span>
            <span class="nav-link">Logout</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_landing_page():
    """Professional landing page with crown logo"""
    # Theme toggle
    render_theme_toggle()

    st.markdown("""
    <div class="landing-container">
        <div style="text-align: center; width: 100%;">
            <div class="crown-logo">
                <div class="crown-icon">👑</div>
                <div class="brand-letter">E</div>
            </div>
            <h1 class="landing-title">EduLLM</h1>
            <div style="text-align: center; width: 100%; display: flex; justify-content: center;">
                <p class="landing-subtitle">
                    Your AI-powered homework companion. Get instant, accurate answers
                    to your school questions using cutting-edge Large Language Model
                    technology.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Start Learning Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button('🚀 Start Learning', type='primary', use_container_width=True, key='start_learning'):
            st.session_state.page = 'login'
            st.rerun()

    # Why Choose EduLLM Section
    st.markdown("""
    <div style="text-align: center; margin: 4rem 0 2rem 0;">
        <h2 style="font-size: 2.5rem; font-weight: 700; color: #333; margin-bottom: 1rem;">
            Why Choose <span style="color: #FFD700;">EduLLM?</span>
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # Flash Cards in Single Row
    st.markdown("""
    <div class="flash-cards">
        <div class="flash-card">
            <div class="flash-card-icon">🧠</div>
            <div class="flash-card-title">AI-Powered Learning</div>
            <div class="flash-card-desc">Advanced LLM technology helps you understand complex concepts with personalized explanations.</div>
        </div>
        <div class="flash-card">
            <div class="flash-card-icon">📖</div>
            <div class="flash-card-title">Multiple Subjects</div>
            <div class="flash-card-desc">Get help with Math, Science, History, English, and more - all in one platform.</div>
        </div>
        <div class="flash-card">
            <div class="flash-card-icon">💡</div>
            <div class="flash-card-title">Instant Solutions</div>
            <div class="flash-card-desc">Get step-by-step solutions to your homework problems in seconds.</div>
        </div>
        <div class="flash-card">
            <div class="flash-card-icon">👥</div>
            <div class="flash-card-title">Student Community</div>
            <div class="flash-card-desc">Join thousands of students who are already improving their grades with EduLLM.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Ready to Ace Section
    st.markdown("""
    <div style="text-align: center; margin: 4rem 0 2rem 0; padding: 3rem 2rem; background: rgba(255, 215, 0, 0.1); border-radius: 20px;">
        <h2 style="font-size: 2rem; font-weight: 700; color: #333; margin-bottom: 1rem;">
            Ready to Ace Your Homework?
        </h2>
        <p style="font-size: 1.1rem; color: #666; max-width: 600px; margin: 0 auto;">
            Join thousands of students who are already using EduLLM to improve their understanding and grades.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Final CTA
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button('🎯 Get Started Today', type='primary', use_container_width=True, key='get_started'):
            st.session_state.page = 'login'
            st.rerun()

def render_login_page():
    """Professional centered login/register page"""
    # Theme toggle
    render_theme_toggle()

    # Centered login container
    st.markdown('<div class="login-page">', unsafe_allow_html=True)

    # Crown logo and title - more compact
    st.markdown("""
    <div class="login-header">
        <div class="crown-logo" style="margin-bottom: 1rem;">
            <div class="crown-icon">👑</div>
            <div class="brand-letter" style="width: 80px; height: 80px; font-size: 2.5rem;">E</div>
        </div>
        <h1 style="font-size: 2rem; font-weight: 700; color: #FFD700; margin: 1rem 0;">Welcome to EduLLM</h1>
        <p style="color: #666; font-size: 1rem; margin-bottom: 0;">Sign in to start learning</p>
    </div>
    """, unsafe_allow_html=True)

    # Centered auth container
    st.markdown('<div class="login-form-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([0.5, 2, 0.5])
    with col2:
        # Tabs
        tab_col1, tab_col2 = st.columns(2)
        with tab_col1:
            if st.button("Login", use_container_width=True, key="login_tab",
                        type="primary" if st.session_state.auth_tab == 'login' else "secondary"):
                st.session_state.auth_tab = 'login'
        with tab_col2:
            if st.button("Sign Up", use_container_width=True, key="register_tab",
                        type="primary" if st.session_state.auth_tab == 'register' else "secondary"):
                st.session_state.auth_tab = 'register'

        st.markdown("---")

        if st.session_state.auth_tab == 'login':
            st.markdown("### Sign In")
            st.markdown("*Enter your credentials to access your account*")
            st.markdown("")

            email = st.text_input("Email", placeholder="student@example.com", key="login_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")

            st.markdown("")
            if st.button("Sign In", type="primary", use_container_width=True):
                if email and password:
                    st.session_state.logged_in = True
                    st.session_state.user_id = email
                    st.session_state.page = 'subjects'
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Please fill in all fields")

            st.markdown("---")
            st.markdown("**OR CONTINUE WITH**")

            google_col, github_col = st.columns(2)
            with google_col:
                if st.button("🔍 Google", use_container_width=True):
                    st.info("Google login coming soon!")
            with github_col:
                if st.button("🐙 GitHub", use_container_width=True):
                    st.info("GitHub login coming soon!")

        else:  # register
            st.markdown("### Create Account")
            st.markdown("*Join thousands of students improving their grades*")
            st.markdown("")

            name = st.text_input("Full Name", placeholder="Enter your full name", key="reg_name")
            email = st.text_input("Email", placeholder="student@example.com", key="reg_email")
            password = st.text_input("Password", type="password", placeholder="Create a password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="reg_confirm")

            st.markdown("")
            if st.button("Create Account", type="primary", use_container_width=True):
                if name and email and password and confirm_password:
                    if password == confirm_password:
                        st.session_state.logged_in = True
                        st.session_state.user_id = email
                        st.session_state.page = 'subjects'
                        st.success("Registration successful!")
                        st.rerun()
                    else:
                        st.error("Passwords don't match")
                else:
                    st.error("Please fill in all fields")

        st.markdown("")
        # Back to landing
        if st.button('← Back to Home', use_container_width=True):
            st.session_state.page = 'landing'
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)  # Close login-form-container
    st.markdown('</div>', unsafe_allow_html=True)  # Close login-page

def render_subjects_page():
    """Subjects grid with navbar"""
    render_theme_toggle()
    render_navbar()

    st.markdown("# 📚 Choose Your Subject")
    st.markdown("**Select a subject to get started with your homework questions**")
    st.markdown("---")

    # Create 3x3 grid
    cols = st.columns(3)
    subjects = list(SUBJECTS.keys())

    for idx, subject in enumerate(subjects):
        with cols[idx % 3]:
            info = SUBJECTS[subject]
            st.markdown(f"### {info['icon']} {subject}")
            st.markdown(f"*{info.get('desc', 'Get expert help with your questions')}*")

            if st.button(f"Select {subject}", key=f"select_{subject}", use_container_width=True, type="primary"):
                st.session_state.selected_subject = subject
                st.session_state.page = 'questions'
                st.rerun()

            st.markdown("")  # Add space

def render_questions_page():
    """Questions page with navbar"""
    render_theme_toggle()
    render_navbar()

    subject = st.session_state.selected_subject
    st.markdown(f"# ❓ {subject} Questions")

    # Back button
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("← Back to Subjects", use_container_width=True):
            st.session_state.page = 'subjects'
            st.rerun()

    st.markdown("---")

    # Question input
    question = st.text_area(
        f"📝 Enter your {subject} question:",
        height=150,
        placeholder=f"Ask your {subject} question here...",
        help="Be specific and include all relevant details"
    )

    if st.button("🎯 Get Solution", type="primary"):
        if question.strip():
            with st.spinner("Getting solution..."):
                response = get_api_response(question, subject)

                if response:
                    st.markdown("---")
                    st.markdown(f"## 📚 {subject} Solution")

                    # Display solution
                    formatted_response = format_response(response)
                    st.markdown(formatted_response)

                    # Feedback
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

def main():
    """Main application with complete workflow"""
    # Load CSS
    load_css()

    # Route to appropriate page
    if st.session_state.page == 'landing':
        render_landing_page()
    elif st.session_state.page == 'login':
        render_login_page()
    elif st.session_state.page == 'subjects':
        if st.session_state.logged_in:
            render_subjects_page()
        else:
            st.session_state.page = 'login'
            st.rerun()
    elif st.session_state.page == 'questions':
        if st.session_state.logged_in and st.session_state.selected_subject:
            render_questions_page()
        else:
            st.session_state.page = 'subjects'
            st.rerun()

if __name__ == "__main__":
    main()