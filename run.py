"""Launcher for the EduLLM Streamlit app (clean 4-page navigation flow).

Navigation Flow: Landing → Login → Subjects → Questions
Run with: streamlit run run.py
"""

# Import local config first to set up database connection
import local_config

import streamlit as st
from app.db import init_db
from app.ui import (
    render_global_css,
    render_landing_page,
    auth_ui,
    render_home_page,
    render_profile_page,
    render_about_page,
    render_navigation,
    render_footer,
)

# Ensure page config is set
st.set_page_config(page_title="EduLLM - AI Study Assistant", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")


def main():
    """Launcher that manages four pages: landing, login, home, profile/about."""
    # Force refresh timestamp: 2025-01-27 - This should force Streamlit Cloud to reload
    init_db()

    # Inject global CSS if available
    try:
        render_global_css()
    except Exception:
        pass

    # Initialize session state defaults
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'landing'
    if 'show_login' not in st.session_state:
        st.session_state['show_login'] = False

    user_logged = bool(st.session_state.get('user_id'))

    # Top navigation for logged-in users
    if user_logged:
        nav_cols = st.columns([1, 1, 1, 1, 6])
        if nav_cols[0].button('Home'):
            st.session_state['current_page'] = 'home'
            st.session_state['selected_subject'] = None
            st.rerun()
        if nav_cols[1].button('Profile'):
            st.session_state['current_page'] = 'profile'
            st.rerun()
        if nav_cols[2].button('About'):
            st.session_state['current_page'] = 'about'
            st.rerun()
        if nav_cols[3].button('Logout'):
            # Clear auth-related state
            for k in ['user_id', 'username', 'access_token', 'selected_subject', 'current_page', 'show_login']:
                if k in st.session_state:
                    del st.session_state[k]
            # After logout, go to landing
            st.session_state['current_page'] = 'landing'
            st.rerun()

    # If a login was requested (from landing or elsewhere), show auth UI
    if st.session_state.get('show_login') or st.session_state.get('current_page') == 'login':
        login_ok = auth_ui()
        if login_ok:
            st.session_state['current_page'] = 'home'
            st.session_state['show_login'] = False
            st.rerun()
        else:
            # If login UI shown but not logged in yet, stop further rendering
            return

    # Not logged in -> landing page
    if not user_logged:
        render_landing_page()

        # Provide functional Streamlit buttons as a fallback to navigate
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button('Login'):
                st.session_state['current_page'] = 'login'
                st.session_state['show_login'] = True
                st.rerun()
        with c2:
            if st.button('About'):
                st.session_state['current_page'] = 'about'
                st.rerun()
        return

    # Logged in - route to pages
    page = st.session_state.get('current_page', 'home')

    if page == 'home':
        render_navigation()
        render_home_page()
        render_footer()
        return

    if page == 'profile':
        render_profile_page()
        render_footer()
        return

    if page == 'about':
        render_about_page()
        render_footer()
        return

    # Fallback to home
    render_navigation()
    render_home_page()
    render_footer()


if __name__ == '__main__':
    main()


