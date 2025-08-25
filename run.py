"""Launcher for the refactored Edullm Streamlit app.

Run with: streamlit run run.py
"""

# Import local config first to set up database connection
import local_config

# Prefer the known-working launcher in hw01.py (contains stable UI+logic)
import hw01
import streamlit as st

# hw01 already sets page config; keep a safe default here as well
st.set_page_config(page_title="Academic Assistant Pro", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")

if __name__ == "__main__":
    # Run the working main from hw01 which contains the stable UI flow
    hw01.main()


