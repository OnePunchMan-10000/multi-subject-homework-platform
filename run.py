"""Launcher for the refactored Edullm Streamlit app.

Run with: streamlit run run.py
"""

# Import local config first to set up database connection
import local_config

from app.main import main
import streamlit as st

# Preserve page config from original app
st.set_page_config(page_title="Academic Assistant Pro", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

if __name__ == "__main__":
    main()


