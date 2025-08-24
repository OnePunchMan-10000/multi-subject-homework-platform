#!/usr/bin/env python3
"""
Test script for the new UI components
"""

import streamlit as st
from app.ui import render_landing_page, render_home_page, render_navigation, render_footer

def test_ui():
    st.set_page_config(page_title="UI Test", page_icon="🧪", layout="wide")
    
    st.title("🧪 UI Component Test")
    
    # Test landing page
    st.header("1. Landing Page")
    render_landing_page()
    
    st.markdown("---")
    
    # Test navigation
    st.header("2. Navigation")
    render_navigation()
    
    st.markdown("---")
    
    # Test home page
    st.header("3. Home Page")
    render_home_page()
    
    st.markdown("---")
    
    # Test footer
    st.header("4. Footer")
    render_footer()

if __name__ == "__main__":
    test_ui()

