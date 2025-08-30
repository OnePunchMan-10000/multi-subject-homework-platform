import streamlit as s 
import requests 
import json 
import matplotlib.pyplot as plt 
import numpy as np 
from io import BytesIO 
import re 
import secrets as pysecrets 
from urllib.parse import urlencode 
import sqlite3 
import hashlib 
import os 
import base64 
from datetime import datetime 
import html 
 
# Page configuration 
st.set_page_config( 
    page_title="Academic Assistant Pro", 
    page_icon="🎓", 
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
 
# Improved CSS with better spacing and fraction formatting 
st.markdown(""" 
<style> 
    /* Hide Streamlit default elements */ 
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    header {visibility: hidden;} 
    .stDeployButton {visibility: hidden;} 
     
    /* Global Background with Black/Gold/Silver Gradient */ 
    .stApp { 
        background: linear-gradient(135deg, #000000 0%, #2C2C2C 25%, #C0C0C0 50%, #FFD700 75%, #C0C0C0 100%); 
        background-attachment: fixed; 
        color: white; 
    } 
     
    /* Enhanced text readability with shadows */ 
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, span, div { 
        color: white !important; 
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8) !important; 
        font-size: 1.1rem !important; /* Increased base font size */ 
    } 
     
    /* Main container with glass effect */ 
    .main .block-container { 
        background: rgba(255, 255, 255, 0.1) !important; 
        backdrop-filter: blur(15px) !important; 
        border-radius: 20px !important; 
        margin: 0 auto !important; 
        padding: 2.5rem !important; 
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important; 
        border: 1px solid rgba(255, 215, 0, 0.3) !important; 
        max-width: 1400px !important; /* Limit width on large screens */ 
        width: 95% !important; /* Use percentage width for responsiveness */ 
    } 
     
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
     
    .nav-item { 
        display: inline-block; 
        margin: 0 20px; 
        padding: 8px 16px; 
        background: rgba(255, 255, 255, 0.15); 
        border: 1px solid rgba(255, 255, 255, 0.3); 
        border-radius: 25px; 
        color: white !important; 
        text-decoration: none; 
        font-weight: 500; 
        font-size: 14px; 
        transition: all 0.3s ease; 
        cursor: pointer; 
    } 
     
    .nav-item:hover { 
        background: rgba(255, 255, 255, 0.25); 
        transform: translateY(-2px); 
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2); 
    } 
     
    .nav-item.active { 
        background: rgba(255, 255, 255, 0.3); 
        border: 1px solid rgba(255, 255, 255, 0.5); 
    } 
     
    /* Footer */ 
    .app-footer { 
        position: fixed; 
        bottom: 0; 
        left: 0; 
        right: 0; 
        background: rgba(0, 0, 0, 0.7); 
        backdrop-filter: blur(10px); 
        padding: 10px 0; 
        text-align: center; 
        color: rgba(255, 255, 255, 0.8); 
        font-size: 12px; 
        z-index: 1000; 
        border-top: 1px solid rgba(255, 255, 255, 0.1); 
    } 
     
    .footer-content { 
        max-width: 1200px; 
        margin: 0 auto; 
        padding: 0 20px; 
    } 
     
    /* Add bottom padding to main content to avoid footer overlap */ 
    .main .block-container { 
        padding-bottom: 60px !important; 
    } 
    
    /* Responsive design for different screen sizes */
    @media (max-width: 1200px) {
        .main .block-container {
            max-width: 95% !important;
            padding: 2rem !important;
        }
        
        .brand-title {
            font-size: 5rem !important;
        }
        
        .flash-cards {
            gap: 1.5rem !important;
        }
    }
    
    @media (max-width: 768px) {
        .main .block-container {
            padding: 1.5rem !important;
            margin: 0.5rem auto !important;
            width: 98% !important;
        }
        
        .brand-title {
            font-size: 3.5rem !important;
        }
        
        .nav-item {
            margin: 0 10px !important;
            padding: 6px 12px !important;
            font-size: 12px !important;
        }
        
        .flash-card {
            min-width: 100% !important;
        }
        
        .logo-letter {
            width: 70px !important;
            height: 70px !important;
            font-size: 2.8rem !important;
        }
    }
    
    @media (max-width: 480px) {
        .brand-title {
            font-size: 2.5rem !important;
        }
        
        .brand-sub {
            font-size: 1.2rem !important;
        }
        
        .nav-menu {
            padding: 10px !important;
            display: flex !important;
            flex-wrap: wrap !important;
            justify-content: center !important;
        }
        
        .nav-item {
            margin: 5px !important;
            font-size: 11px !important;
        }
        
        .logo-letter {
            width: 50px !important;
            height: 50px !important;
            font-size: 2rem !important;
        }
    }
     
    /* Brand styling with crown */ 
    .brand-title { 
        font-size: 6.5rem; 
        margin: 0.5rem 0 0.3rem 0; 
        line-height: 1.05; 
        background: linear-gradient(135deg, #FFD700 0%, #C0C0C0 30%, #FFD700 60%, #C0C0C0 100%); 
        -webkit-background-clip: text; background-clip: text; color: transparent; 
        -webkit-text-stroke: 2px rgba(0,0,0,0.35); 
        text-shadow: 
            0 2px 0 rgba(255,255,255,0.25), 
            0 6px 12px rgba(0,0,0,0.45), 
            0 16px 28px rgba(0,0,0,0.35), 
            0 0 40px rgba(212, 175, 55, 0.3), 
            0 0 60px rgba(192, 192, 192, 0.25); 
        filter: drop-shadow(0 12px 28px rgba(0,0,0,0.4)); 
        letter-spacing: 0.8px; 
    } 
    .brand-sub { 
        margin-top: 0.5rem; 
        opacity: 0.96; 
        text-shadow: 0 1px 6px rgba(0,0,0,0.3); 
        font-size: 1.8rem; 
    } 
     
    /* Logo styling */ 
    .logo-container { 
        position: relative; 
        display: inline-block; 
        margin-bottom: 20px; 
    } 
     
    .crown-icon { 
        position: absolute; 
        top: -30px; 
        left: 50%; 
        transform: translateX(-50%); 
        font-size: 3rem; 
        color: #FFD700; 
        text-shadow: 0 2px 5px rgba(0,0,0,0.5); 
    } 
     
    .logo-letters { 
        display: flex; 
        justify-content: center; 
    } 
     
    .logo-letter { 
        width: 90px; 
        height: 90px; 
        background: linear-gradient(135deg, #FFD700, #C0C0C0); 
        border-radius: 15px; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        font-size: 3.5rem; 
        font-weight: 900; 
        color: #000; 
        margin: 0 8px; 
        box-shadow: 0 8px 20px rgba(0,0,0,0.4); 
        border: 2px solid rgba(255,255,255,0.2); 
    } 
     
    /* Improved solution content styling with better spacing */ 
    .solution-content { 
        background-color: rgba(255,255,255,0.05); 
        border-left: 4px solid #4CAF50; 
        padding: 2rem; 
        margin: 1.5rem 0; 
        border-radius: 8px; 
        line-height: 1.8; 
    } 
     
    .solution-content h3 { 
        color: #4CAF50; 
        margin: 2rem 0 1rem 0; 
        font-size: 1.3em; 
        border-bottom: 2px solid #4CAF50; 
        padding-bottom: 0.5rem; 
    } 
     
    .solution-content p { 
        margin: 1.2rem 0; 
        line-height: 1.8; 
        color: #e0e0e0; 
        font-size: 1.05em; 
    } 
     
    /* Better mathematical expression styling */ 
    .math-line { 
        font-family: 'Courier New', monospace; 
        background-color: rgba(255,193,7,0.15); 
        padding: 1rem 1.5rem; 
        margin: 1rem 0; 
        border-radius: 6px; 
        color: #ffc107; 
        text-align: center; 
        font-size: 1.1em; 
        line-height: 1.6; 
        border: 1px solid rgba(255,193,7,0.3); 
    } 
     
    /* Fraction display within math-line - ensure proper vertical display */ 
    .fraction-display { 
        display: inline-block; 
        text-align: center; 
        margin: 0 8px; 
        vertical-align: middle; 
        line-height: 1.2; 
    } 
     
    .fraction-bar { 
        border-bottom: 2px solid #ffc107; 
        margin: 2px 0; 
        line-height: 1; 
        width: 100%; 
    } 
     
    /* Superscript styling for powers */ 
    .power { 
        font-size: 0.8em; 
        vertical-align: super; 
        line-height: 0; 
    } 
     
    .final-answer { 
        background-color: rgba(76,175,80,0.2); 
        border: 2px solid rgba(76,175,80,0.4); 
        padding: 1.5rem; 
        margin: 1.5rem 0; 
        border-radius: 8px; 
        text-align: center; 
        font-weight: bold; 
        font-size: 1.2em; 
    } 
     
    /* Flash Cards */ 
    .flash-cards { 
        display: flex; 
        justify-content: center; 
        gap: 2rem; 
        margin: 3rem auto; 
        flex-wrap: wrap; 
        max-width: 1400px; 
    } 
     
    .flash-card { 
        background: rgba(255, 255, 255, 0.1); 
        backdrop-filter: blur(10px); 
        padding: 2rem; 
        border-radius: 15px; 
        text-align: center; 
        box-shadow: 0 8px 25px rgba(0,0,0,0.2); 
        border: 1px solid rgba(255, 215, 0, 0.2); 
        transition: all 0.3s ease; 
        flex: 1; 
        min-width: 250px; 
        max-width: 300px; /* Slightly wider cards */ 
    } 
     
    .flash-card:hover { 
        transform: translateY(-10px); 
        box-shadow: 0 15px 35px rgba(255, 215, 0, 0.3); 
        border-color: #FFD700; 
    } 
     
    .flash-card-icon { 
        font-size: 3rem; 
        margin-bottom: 1rem; 
        color: #FFD700; 
    } 
     
    .flash-card-title { 
        font-size: 1.3rem; 
        font-weight: 600; 
        margin-bottom: 1rem; 
    } 
     
    .flash-card-desc { 
        font-size: 0.95rem; 
        line-height: 1.5; 
        color: rgba(255, 255, 255, 0.8); 
    } 
     
    /* Auth Container */ 
    .auth-container { 
        max-width: 450px; 
        margin: 2rem auto; 
        background: rgba(255, 255, 255, 0.1); 
        backdrop-filter: blur(15px); 
        border-radius: 20px; 
        box-shadow: 0 15px 50px rgba(0,0,0,0.3); 
        overflow: hidden; 
        border: 1px solid rgba(255, 215, 0, 0.3); 
    } 
     
    .auth-tabs { 
        display: flex; 
        background: rgba(0, 0, 0, 0.2); 
    } 
     
    .auth-tab { 
        flex: 1; 
        padding: 1rem; 
        text-align: center; 
        cursor: pointer; 
        font-weight: 600; 
        transition: all 0.3s ease; 
        color: white; 
    } 
     
    .auth-tab.active { 
        background: linear-gradient(135deg, #FFD700, #C0C0C0); 
        color: black; 
    } 
     
    .auth-form { 
        padding: 2.5rem; 
    } 
     
    /* Input styling */
    .stTextInput > div > div > input {
        background-color: rgba(255,255,255,0.9) !important;
        border: 2px solid rgba(255,255,255,0.5) !important;
        border-radius: 8px !important;
        color: #333 !important;
        padding: 8px 12px !important;
        font-size: 14px !important;
        max-width: 300px !important;
    }
    
    .stTextArea textarea {
        background-color: rgba(255,255,255,0.9) !important;
        border: 2px solid rgba(255,255,255,0.5) !important;
        border-radius: 8px !important;
        color: #333 !important;
        padding: 8px 12px !important;
        font-size: 14px !important;
        max-width: 400px !important;
        min-height: 80px !important;
        max-height: 200px !important;
    }

    /* Enhanced Button Styling */ 
    .stButton > button { 
        background: linear-gradient(45deg, #FFD700, #C0C0C0) !important; 
        color: #000000 !important; 
        border: none !important; 
        border-radius: 10px !important; 
        padding: 0.75rem 1.5rem !important; 
        font-weight: 600 !important; 
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important; 
        transition: all 0.3s ease !important; 
    } 
     
    .stButton > button:hover { 
        background: linear-gradient(45deg, #C0C0C0, #FFD700) !important; 
        transform: translateY(-2px) !important; 
        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4) !important; 
    } 
</style> 
""", unsafe_allow_html=True) 

# Define subjects
SUBJECTS = {
    "Mathematics": {"icon": "📐", "description": "Algebra, Calculus, Geometry, Statistics"},
    "Physics": {"icon": "🔭", "description": "Mechanics, Thermodynamics, Electromagnetism"},
    "Chemistry": {"icon": "⚗️", "description": "Organic, Inorganic, Physical Chemistry"},
    "Biology": {"icon": "🧬", "description": "Cell Biology, Genetics, Ecology"},
    "Computer Science": {"icon": "💻", "description": "Programming, Algorithms, Data Structures"},
    "Economics": {"icon": "📊", "description": "Micro, Macro, Econometrics"},
    "English": {"icon": "📖", "description": "Literature, Grammar, Writing"},
    "History": {"icon": "📜", "description": "World History, Analysis, Research"},
    "Geography": {"icon": "🌍", "description": "Physical, Human, Environmental"}
}

# Footer component
def render_footer():
    st.markdown("""
    <div class="app-footer">
        <div class="footer-content">
            © 2025 Academic Assistant Pro. All rights reserved. | 
            Empowering students with AI-powered homework solutions.
        </div>
    </div>
    """, unsafe_allow_html=True)

# Navigation component
def render_navigation():
    if st.session_state.logged_in:
        st.markdown("""
        <div class="nav-menu">
            <a class="nav-item" href="javascript:void(0);" onclick="navigateTo('home')" aria-label="Home">🏠 Home</a>
            <a class="nav-item" href="javascript:void(0);" onclick="navigateTo('subjects')" aria-label="Subjects">📚 Subjects</a>
            <a class="nav-item" href="javascript:void(0);" onclick="navigateTo('profile')" aria-label="Profile">👤 Profile</a>
            <a class="nav-item" href="javascript:void(0);" onclick="navigateTo('about')" aria-label="About">ℹ️ About</a>
            <a class="nav-item" href="javascript:void(0);" onclick="logout()" aria-label="Logout">🚪 Logout</a>
        </div>
        
        <script type="text/javascript">
        function navigateTo(page) {
            if (window.parent) {
                window.parent.postMessage({type: 'navigateTo', page: page}, '*');
            }
        }
        
        function logout() {
            if (window.parent) {
                window.parent.postMessage({type: 'logout'}, '*');
            }
        }
        </script>
        """, unsafe_allow_html=True)

# Landing page
def render_landing_page():
    # Logo with AE and crown
    st.markdown("""
    <div style="text-align: center; padding-top: 2rem;">
        <div class="logo-container">
            <div class="crown-icon">👑</div>
            <div class="logo-letters">
                <div class="logo-letter">A</div>
                <div class="logo-letter">E</div>
            </div>
        </div>
        <h1 class="brand-title">Academic Assistant Pro</h1>
        <p class="brand-sub">Your AI-powered homework companion</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main description
    st.markdown("""
    <div style="text-align: center; max-width: 900px; margin: 2rem auto;">
        <p style="font-size: 1.3rem; line-height: 1.7;">
            Get instant, step-by-step solutions to your homework problems across multiple subjects.
            Our advanced AI provides detailed explanations that help you understand concepts, not just memorize answers.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button('🚀 Start Learning Now', use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()
    
    # Flash Cards
    st.markdown("""
    <h2 style="text-align: center; margin-top: 3rem;">Why Choose Academic Assistant Pro?</h2>
    
    <div class="flash-cards">
        <div class="flash-card">
            <div class="flash-card-icon">🧠</div>
            <div class="flash-card-title">AI-Powered Learning</div>
            <div class="flash-card-desc">Advanced AI technology helps you understand complex concepts with personalized explanations.</div>
        </div>
        
        <div class="flash-card">
            <div class="flash-card-icon">📚</div>
            <div class="flash-card-title">Multiple Subjects</div>
            <div class="flash-card-desc">Get help with Math, Science, History, English, and more - all in one platform.</div>
        </div>
        
        <div class="flash-card">
            <div class="flash-card-icon">⚡</div>
            <div class="flash-card-title">Instant Solutions</div>
            <div class="flash-card-desc">Get step-by-step solutions to your homework problems in seconds.</div>
        </div>
        
        <div class="flash-card">
            <div class="flash-card-icon">📊</div>
            <div class="flash-card-title">Visual Learning</div>
            <div class="flash-card-desc">Complex concepts explained with interactive visualizations and diagrams.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Testimonials
    st.markdown("""
    <div style="text-align: center; margin-top: 4rem;">
        <h2>What Students Say</h2>
        <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 2rem; flex-wrap: wrap;">
            <div style="background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 15px; max-width: 300px;">
                <div style="font-size: 1.5rem; margin-bottom: 1rem;">⭐⭐⭐⭐⭐</div>
                <p style="font-style: italic;">"Academic Assistant Pro helped me understand calculus when I was struggling. The step-by-step explanations are amazing!"</p>
                <p style="margin-top: 1rem; font-weight: bold;">- Sarah J., College Student</p>
            </div>
            <div style="background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 15px; max-width: 300px;">
                <div style="font-size: 1.5rem; margin-bottom: 1rem;">⭐⭐⭐⭐⭐</div>
                <p style="font-style: italic;">"I use this for all my science homework. It explains concepts better than my textbooks do!"</p>
                <p style="margin-top: 1rem; font-weight: bold;">- Michael T., High School Student</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Final CTA
    st.markdown("""
    <div style="text-align: center; margin-top: 4rem; background: linear-gradient(135deg, rgba(255,215,0,0.2), rgba(192,192,192,0.2)); padding: 2rem; border-radius: 15px;">
        <h2>Ready to Ace Your Homework?</h2>
        <p style="margin: 1rem 0 2rem 0;">Join thousands of students who are already improving their grades with Academic Assistant Pro.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button('🎯 Get Started Today', use_container_width=True, key="get_started"):
            st.session_state.page = 'login'
            st.rerun()

# Login page
def render_login_page():
    # Logo with AE and crown (smaller version)
    st.markdown("""
    <div style="text-align: center; padding-top: 1rem;">
        <div class="logo-container" style="transform: scale(0.8);">
            <div class="crown-icon">👑</div>
            <div class="logo-letters">
                <div class="logo-letter">A</div>
                <div class="logo-letter">E</div>
            </div>
        </div>
        <h2 style="font-size: 2rem; margin: 1rem 0;">Welcome to Academic Assistant Pro</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Auth container with tabs
    st.markdown("""
    <div class="auth-container">
        <div class="auth-tabs">
            <div class="auth-tab active" id="login-tab" onclick="switchTab('login')">Login</div>
            <div class="auth-tab" id="register-tab" onclick="switchTab('register')">Sign Up</div>
        </div>
        <div class="auth-form" id="login-form">
            <div id="login-content"></div>
        </div>
        <div class="auth-form" id="register-form" style="display: none;">
            <div id="register-content"></div>
        </div>
    </div>
    
    <script>
    function switchTab(tab) {
        if (tab === 'login') {
            document.getElementById('login-tab').classList.add('active');
            document.getElementById('register-tab').classList.remove('active');
            document.getElementById('login-form').style.display = 'block';
            document.getElementById('register-form').style.display = 'none';
            window.parent.postMessage({type: 'switchAuthTab', tab: 'login'}, '*');
        } else {
            document.getElementById('login-tab').classList.remove('active');
            document.getElementById('register-tab').classList.add('active');
            document.getElementById('login-form').style.display = 'none';
            document.getElementById('register-form').style.display = 'block';
            window.parent.postMessage({type: 'switchAuthTab', tab: 'register'}, '*');
        }
    }
    </script>
    """, unsafe_allow_html=True)
    
    # Login Form
    login_form_placeholder = st.empty()
    with login_form_placeholder.container():
        if st.session_state.auth_tab == 'login':
            st.markdown("<div id='login-content'></div>", unsafe_allow_html=True)
            email = st.text_input("Email Address", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Sign In", use_container_width=True, key="login_button"):
                # Here you would add authentication logic
                st.session_state.logged_in = True
                st.session_state.page = 'subjects'
                st.rerun()
            
            st.markdown("""
            <div style="text-align: center; margin-top: 1rem;">
                <a href="#" style="color: #FFD700; text-decoration: none;">Forgot password?</a>
            </div>
            """, unsafe_allow_html=True)
    
    # Register Form
    register_form_placeholder = st.empty()
    with register_form_placeholder.container():
        if st.session_state.auth_tab == 'register':
            st.markdown("<div id='register-content'></div>", unsafe_allow_html=True)
            name = st.text_input("Full Name", key="register_name")
            email = st.text_input("Email Address", key="register_email")
            password = st.text_input("Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm")
            if st.button("Create Account", use_container_width=True, key="register_button"):
                # Here you would add registration logic
                st.session_state.logged_in = True
                st.session_state.page = 'subjects'
                st.rerun()
    
    # Tab switching logic
    if st.session_state.auth_tab == 'login':
        register_form_placeholder.empty()
    else:
        login_form_placeholder.empty()
    
    # Switch tab buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Switch to Login", key="switch_login", use_container_width=True):
            st.session_state.auth_tab = 'login'
            st.rerun()
    with col2:
        if st.button("Switch to Register", key="switch_register", use_container_width=True):
            st.session_state.auth_tab = 'register'
            st.rerun()

# Subject grid
def render_subject_grid():
    st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>Select a Subject</h1>", unsafe_allow_html=True)
    
    # Create a grid of subjects
    cols = st.columns(3)
    for i, (subject, details) in enumerate(SUBJECTS.items()):
        with cols[i % 3]:
            # Create a clickable button for each subject with improved styling
            if st.button(f"{details['icon']} {subject}", key=f"subject_{subject}", use_container_width=True):
                st.session_state.selected_subject = subject
                st.rerun()
            
            # Display description below button with better spacing
            st.markdown(f"<p style='color: rgba(255,255,255,0.7); margin-bottom: 2rem; font-size: 0.9rem;'>{details['description']}</p>", unsafe_allow_html=True)

# Question page
def render_question_page():
    subject = st.session_state.selected_subject
    
    st.markdown(f"<h1 style='font-size: 2.5rem;'>{SUBJECTS[subject]['icon']} {subject} Question</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.3rem;'><strong>Ask your question and get a detailed step-by-step solution</strong></p>", unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Subjects", key="back_to_subjects"):
        st.session_state.selected_subject = None
        st.rerun()
    
    st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
    
    # Question input
    question = st.text_area(
        f"📝 Enter your {subject} question:",
        height=150,
        placeholder=f"Example: Solve the equation 2x + 5 = 13, or explain photosynthesis...",
        help="Be specific and include all relevant details for the best solution"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎯 Get Solution", type="primary", use_container_width=True, key="get_solution"):
            if question.strip():
                with st.spinner("Getting solution..."):
                    # Here you would call your API to get the solution
                    # For demo purposes, we'll just show a placeholder
                    st.markdown("<hr style='margin: 1.5rem 0;'>", unsafe_allow_html=True)
                    st.markdown(f"<h2 style='font-size: 2rem;'>📚 {subject} Solution</h2>", unsafe_allow_html=True)
                    
                    # Display solution in a clean container
                    st.markdown("""
                    <div class="solution-content">
                        <h3>Understanding the Problem</h3>
                        <p>Let's break down this problem step by step...</p>
                        
                        <h3>Step-by-Step Solution</h3>
                        <p>First, we need to identify the key components...</p>
                        
                        <div class="math-line">2x + 5 = 13</div>
                        <div class="math-line">2x = 13 - 5</div>
                        <div class="math-line">2x = 8</div>
                        <div class="math-line">x = 4</div>
                        
                        <h3>Verification</h3>
                        <p>Let's verify our answer by substituting x = 4 back into the original equation:</p>
                        
                        <div class="math-line">2(4) + 5 = 8 + 5 = 13 ✓</div>
                        
                        <div class="final-answer">Therefore, x = 4 is the solution.</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show diagram
                    st.markdown("<h3 style='font-size: 1.5rem; margin-top: 2rem;'>📊 Visualization</h3>", unsafe_allow_html=True)
                    
                    # Create a simple visualization
                    fig, ax = plt.subplots(figsize=(10, 6))
                    x = np.linspace(0, 8, 100)
                    y1 = 2*x + 5
                    y2 = np.ones_like(x) * 13
                    ax.plot(x, y1, 'b-', linewidth=3, label='2x + 5')
                    ax.plot(x, y2, 'r-', linewidth=3, label='13')
                    ax.plot(4, 13, 'go', markersize=12, label='Solution (4, 13)')
                    ax.set_xlabel('x', fontsize=14)
                    ax.set_ylabel('y', fontsize=14)
                    ax.set_title('Graphical Solution of 2x + 5 = 13', fontsize=16)
                    ax.grid(True, alpha=0.3)
                    ax.legend(fontsize=12)
                    
                    # Convert plot to image
                    buf = BytesIO()
                    fig.savefig(buf, format="png", dpi=120, bbox_inches='tight')
                    buf.seek(0)
                    st.image(buf, use_container_width=True)
                    
                    # Simple feedback
                    st.markdown("<h3 style='font-size: 1.5rem; margin-top: 2rem;'>Rate this solution</h3>", unsafe_allow_html=True)
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if st.button("👍 Helpful", key="helpful"):
                            st.success("Thanks for your feedback!")
                    with col_b:
                        if st.button("👎 Needs work", key="needs_work"):
                            st.info("We'll improve our solutions!")
                    with col_c:
                        if st.button("🔄 Try again", key="try_again"):
                            st.rerun()
                    
                    # History section
                    st.markdown("<hr style='margin: 3rem 0 1.5rem 0;'>", unsafe_allow_html=True)
                    st.markdown("<h2 style='font-size: 1.8rem;'>📜 Your Question History</h2>", unsafe_allow_html=True)
                    
                    # Sample history entries
                    history_entries = [
                        {"question": "Solve the equation 2x + 5 = 13", "date": "Today, 10:30 AM", "subject": subject},
                        {"question": "What is the derivative of f(x) = x^2 + 3x - 5?", "date": "Yesterday, 3:15 PM", "subject": subject},
                        {"question": "Explain the Pythagorean theorem", "date": "3 days ago", "subject": subject}
                    ]
                    
                    for entry in history_entries:
                        with st.expander(f"{entry['question']} - {entry['date']}"):
                            st.markdown(f"**Subject:** {entry['subject']}")
                            st.markdown(f"**Question:** {entry['question']}")
                            st.markdown("**Status:** Answered")
                            if st.button("View Solution", key=f"view_{hash(entry['question'])}"):
                                st.info("Loading previous solution...")
            else:
                st.warning("Please enter a question.")
    
    # If no solution is shown yet, display sample history at the bottom
    if 'get_solution' not in st.session_state:
        st.markdown("<hr style='margin: 3rem 0 1.5rem 0;'>", unsafe_allow_html=True)
        st.markdown("<h2 style='font-size: 1.8rem;'>📜 Your Recent Questions</h2>", unsafe_allow_html=True)
        
        # Sample history entries
        recent_entries = [
            {"question": "What is the law of conservation of energy?", "date": "2 days ago", "subject": "Physics"},
            {"question": "Explain the process of photosynthesis", "date": "Last week", "subject": "Biology"},
            {"question": "Solve the quadratic equation x^2 - 4x + 4 = 0", "date": "Last week", "subject": "Mathematics"}
        ]
        
        for entry in recent_entries:
            with st.expander(f"{entry['question']} - {entry['date']}"):
                st.markdown(f"**Subject:** {entry['subject']}")
                st.markdown(f"**Question:** {entry['question']}")
                st.markdown("**Status:** Answered")
                if st.button("View Solution", key=f"view_recent_{hash(entry['question'])}"):
                    st.info("Loading previous solution...")

# About page
def render_about_page():
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <div class="logo-container">
            <div class="crown-icon">👑</div>
            <div class="logo-letters">
                <div class="logo-letter">A</div>
                <div class="logo-letter">E</div>
            </div>
        </div>
        <h1>About Academic Assistant Pro</h1>
        <p style="max-width: 700px; margin: 1rem auto; line-height: 1.6;">
            We're revolutionizing education by making high-quality, personalized learning
            assistance accessible to every student through the power of artificial intelligence.
        </p>
    </div>
    
    <div style="margin: 2rem 0;">
        <h2>Our Mission</h2>
        <p>
            At Academic Assistant Pro, we believe that every student deserves access to personalized, high-quality
            educational support. Our mission is to democratize learning by providing an AI-powered
            homework assistant that helps students understand complex concepts, complete assignments, and
            build confidence in their academic abilities.
        </p>
    </div>
    
    <div style="margin: 2rem 0;">
        <h2>Why Choose Academic Assistant Pro?</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin-top: 2rem;">
            <div>
                <h3>🤖 AI-Powered Learning</h3>
                <p>Our advanced AI understands your questions and provides detailed, step-by-step explanations
                that help you learn, not just get answers.</p>
            </div>
            <div>
                <h3>📚 Multi-Subject Support</h3>
                <p>From Mathematics to Literature, Chemistry to History - we cover all major academic subjects
                with specialized knowledge in each area.</p>
            </div>
            <div>
                <h3>⚡ Instant Help</h3>
                <p>Get help whenever you need it. Our AI tutor is available 24/7 to assist with your homework
                and study questions.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Profile page
def render_profile_page():
    st.markdown("<h1 style='font-size: 2.5rem;'>👤 User Profile</h1>", unsafe_allow_html=True)
    
    # User info
    st.markdown("""
    <div style="background: rgba(255,255,255,0.1); padding: 2rem; border-radius: 15px; margin: 2rem 0;">
        <h3>👋 Welcome back!</h3>
        <p><strong>Username:</strong> Student123</p>
        <p><strong>Member since:</strong> January 2025</p>
        <p><strong>Questions solved:</strong> 42</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Usage stats
    st.markdown("<h2 style='font-size: 1.8rem;'>📊 Your Usage Statistics</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem;">
            <h3>Most Used Subjects</h3>
            <ol>
                <li>Mathematics (15 questions)</li>
                <li>Physics (10 questions)</li>
                <li>Chemistry (8 questions)</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: rgba(255,255,255,0.1); padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem;">
            <h3>Recent Activity</h3>
            <ul>
                <li>Solved a Calculus problem (2 hours ago)</li>
                <li>Viewed Physics solution (1 day ago)</li>
                <li>Asked a Chemistry question (3 days ago)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Question History Section
    st.markdown("<h2 style='font-size: 1.8rem; margin-top: 2rem;'>📜 Your Question History</h2>", unsafe_allow_html=True)
    
    # Sample history entries
    history_entries = [
        {"question": "Solve the equation 2x + 5 = 13", "date": "Today, 10:30 AM", "subject": "Mathematics"},
        {"question": "What is the derivative of f(x) = x^2 + 3x - 5?", "date": "Yesterday, 3:15 PM", "subject": "Mathematics"},
        {"question": "Explain the Pythagorean theorem", "date": "3 days ago", "subject": "Mathematics"},
        {"question": "What is the law of conservation of energy?", "date": "Last week", "subject": "Physics"},
        {"question": "Explain the process of photosynthesis", "date": "Last week", "subject": "Biology"},
        {"question": "Solve the quadratic equation x^2 - 4x + 4 = 0", "date": "2 weeks ago", "subject": "Mathematics"}
    ]
    
    # Create tabs for different history views
    all_tab, math_tab, science_tab = st.tabs(["All Questions", "Mathematics", "Science"])
    
    with all_tab:
        for entry in history_entries:
            with st.expander(f"{entry['question']} - {entry['date']}"):
                st.markdown(f"**Subject:** {entry['subject']}")
                st.markdown(f"**Question:** {entry['question']}")
                st.markdown("**Status:** Answered")
                if st.button("View Solution", key=f"view_all_{hash(entry['question'])}"):
                    st.info("Loading previous solution...")
    
    with math_tab:
        math_entries = [entry for entry in history_entries if entry['subject'] == 'Mathematics']
        for entry in math_entries:
            with st.expander(f"{entry['question']} - {entry['date']}"):
                st.markdown(f"**Subject:** {entry['subject']}")
                st.markdown(f"**Question:** {entry['question']}")
                st.markdown("**Status:** Answered")
                if st.button("View Solution", key=f"view_math_{hash(entry['question'])}"):
                    st.info("Loading previous solution...")
    
    with science_tab:
        science_entries = [entry for entry in history_entries if entry['subject'] in ['Physics', 'Biology', 'Chemistry']]
        for entry in science_entries:
            with st.expander(f"{entry['question']} - {entry['date']}"):
                st.markdown(f"**Subject:** {entry['subject']}")
                st.markdown(f"**Question:** {entry['question']}")
                st.markdown("**Status:** Answered")
                if st.button("View Solution", key=f"view_science_{hash(entry['question'])}"):
                    st.info("Loading previous solution...")
    
    # Pagination controls
    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        prev_col, page_col, next_col = st.columns(3)
        with prev_col:
            st.button("« Previous", key="prev_page", use_container_width=True)
        with page_col:
            st.markdown("<p style='text-align: center;'>Page 1 of 3</p>", unsafe_allow_html=True)
        with next_col:
            st.button("Next »", key="next_page", use_container_width=True)

# Main app logic
def main():
    # Handle page routing
    if st.session_state.page == 'landing':
        render_landing_page()
    elif st.session_state.page == 'login':
        render_login_page()
    elif st.session_state.logged_in:
        # Only show navigation when logged in
        render_navigation()
        
        if st.session_state.page == 'subjects':
            if st.session_state.selected_subject:
                render_question_page()
            else:
                render_subject_grid()
        elif st.session_state.page == 'profile':
            render_profile_page()
        elif st.session_state.page == 'about':
            render_about_page()
    else:
        # Redirect to login if not logged in
        st.session_state.page = 'login'
        st.rerun()
    
    # Always render footer
    render_footer()

# JavaScript event handlers
st.markdown("""
<script type="text/javascript">
// Listen for messages from components
window.addEventListener('message', function(event) {
    const data = event.data;
    
    if (data && data.type) {
        if (data.type === 'navigateTo') {
            // Handle navigation
            window.parent.postMessage({type: 'streamlitEvent', name: 'navigateTo', data: data.page}, '*');
        } else if (data.type === 'logout') {
            // Handle logout
            window.parent.postMessage({type: 'streamlitEvent', name: 'logout'}, '*');
        } else if (data.type === 'selectSubject') {
            // Handle subject selection
            window.parent.postMessage({type: 'streamlitEvent', name: 'selectSubject', data: data.subject}, '*');
        } else if (data.type === 'switchAuthTab') {
            // Handle auth tab switching
            window.parent.postMessage({type: 'streamlitEvent', name: 'switchAuthTab', data: data.tab}, '*');
        }
    }
});
</script>
""", unsafe_allow_html=True)

# Handle Streamlit events
if st.session_state.get('streamlit_event'):
    event = st.session_state.streamlit_event
    if event['name'] == 'navigateTo':
        st.session_state.page = event['data']
    elif event['name'] == 'logout':
        st.session_state.logged_in = False
        st.session_state.page = 'landing'
    elif event['name'] == 'selectSubject':
        st.session_state.selected_subject = event['data']
    elif event['name'] == 'switchAuthTab':
        st.session_state.auth_tab = event['data']
    
    # Clear the event after processing
    st.session_state.streamlit_event = None

# Run the app
if __name__ == "__main__":
    main()
