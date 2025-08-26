"""Simple test version of the landing page to preview the design"""

import streamlit as st

# Set page config
st.set_page_config(page_title="EduLLM - Test Landing", page_icon="🎓", layout="wide")

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
            st.success("Button works! This will go to login page.")
        
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
            st.success("This will go to login page! Design looks perfect!")

# Main app
def main():
    st.markdown("# 🎨 Landing Page Preview")
    st.markdown("This is how your landing page will look:")
    st.markdown("---")
    render_landing_page()

if __name__ == '__main__':
    main()

