"""Launcher for the refactored Edullm Streamlit app.

Run with: streamlit run run.py
"""

# Import local config first to set up database connection
import local_config

import streamlit as st
from app import main as app_main


def main():
    """Run the launcher UI (landing/login) then delegate to app.main."""
    # Ensure page config is set before rendering any UI
    st.set_page_config(page_title="Academic Assistant Pro", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

    # Show simple landing page if not logged in
    if not st.session_state.get("user_id"):
        st.header('Welcome to EduLLM')
        st.write('Your AI-powered study companion')
        if st.button('Login to Continue'):
            st.session_state['show_login'] = True
            st.rerun()
        return

    # Run the app's main entrypoint from app.main
    try:
        app_main.main()
    except Exception as e:
        st.error(f'Failed to start the main app: {e}')


if __name__ == "__main__":
    main()


