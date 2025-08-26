"""EduLLM with Professional Frontend UI"""

import streamlit as st
import streamlit.components.v1 as components
import os
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="EduLLM - AI Study Assistant", 
    page_icon="🎓", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

def load_frontend():
    """Load the professional frontend HTML/CSS/JS"""
    
    # Get the path to frontend files
    frontend_path = Path(__file__).parent / "frontend"
    
    # Try to load the fixed version first, then fallback to regular
    html_files = ["index-fixed.html", "index.html"]
    html_content = None
    
    for html_file in html_files:
        html_path = frontend_path / html_file
        if html_path.exists():
            try:
                html_content = html_path.read_text(encoding='utf-8')
                
                # Update relative paths to work with Streamlit
                base_path = f"/app/static/"  # Streamlit static file path
                
                # Replace relative paths with absolute paths
                html_content = html_content.replace('href="css/', f'href="{base_path}css/')
                html_content = html_content.replace('src="js/', f'src="{base_path}js/')
                
                break
            except Exception as e:
                st.error(f"Error loading {html_file}: {e}")
                continue
    
    if html_content:
        # Render the HTML content
        components.html(html_content, height=800, scrolling=True)
    else:
        # Fallback UI if frontend files aren't available
        render_fallback_ui()

def render_fallback_ui():
    """Fallback UI if frontend files can't be loaded"""
    
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px;">
        <div style="display: inline-block; position: relative; margin-bottom: 30px;">
            <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #F4C430, #FFA500); 
                        border-radius: 16px; display: flex; align-items: center; justify-content: center; 
                        font-size: 2.5rem; font-weight: 800; color: white; margin: 0 auto;">
                <span style="position: absolute; top: -15px; font-size: 2rem;">👑</span>
                E
            </div>
        </div>
        
        <h1 style="color: #F4C430; font-size: 3.5rem; margin: 20px 0; font-weight: 800;">EduLLM</h1>
        <p style="color: #666; font-size: 1.3rem; margin-bottom: 40px; max-width: 600px; margin-left: auto; margin-right: auto;">
            Your AI-powered homework companion. Get instant, accurate answers to your school questions.
        </p>
        
        <div style="margin: 40px 0;">
            <p style="background: #fff3cd; color: #856404; padding: 15px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #ffeaa7;">
                ⚠️ <strong>Frontend files not found</strong><br>
                The professional UI files should be in the <code>frontend/</code> directory.
            </p>
        </div>
        
        <div style="margin-top: 40px;">
            <h3 style="color: #333; margin-bottom: 20px;">🎯 Expected File Structure:</h3>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: left; display: inline-block;">
                <pre style="margin: 0; font-family: 'Courier New', monospace;">
frontend/
├── index.html or index-fixed.html
├── css/
│   ├── main.css
│   ├── components.css
│   ├── responsive.css
│   └── edullm-design.css
└── js/
    ├── main.js
    ├── api.js
    └── components.js
                </pre>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application entry point"""
    
    # Hide Streamlit default elements
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    # Load the professional frontend
    load_frontend()

if __name__ == '__main__':
    main()
