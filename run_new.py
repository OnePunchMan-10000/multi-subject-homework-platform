"""EduLLM - Professional Frontend Version"""

import streamlit as st
import streamlit.components.v1 as components

# Set page config
st.set_page_config(
    page_title="EduLLM - AI Study Assistant", 
    page_icon="🎓", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

def main():
    """Main application with embedded professional frontend"""
    
    # Hide Streamlit default elements for cleaner look
    hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    div.stToolbar {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    # Embed the professional frontend directly
    frontend_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EduLLM - AI Study Assistant</title>
        
        <!-- Google Fonts -->
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        
        <!-- Font Awesome Icons -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        
        <style>
            /* Embedded CSS - Professional EduLLM Design */
            :root {
                --primary-gold: #F4C430;
                --accent-orange: #FFA500;
                --dark-bg: #1a1a1a;
                --dark-card: #2d2d2d;
                --dark-border: #404040;
                --text-primary: #1f2937;
                --text-secondary: #6b7280;
                --text-white: #ffffff;
                --background: #ffffff;
                --dark-text-primary: #ffffff;
                --dark-text-secondary: #cccccc;
                --dark-text-muted: #999999;
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                line-height: 1.6;
                color: var(--text-primary);
                background: var(--background);
            }
            
            .app-container {
                min-height: 100vh;
                background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            }
            
            .landing-hero {
                padding: 80px 20px 120px 20px;
                text-align: center;
                position: relative;
                overflow: hidden;
            }
            
            .brand-logo {
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 2rem;
                position: relative;
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
                background: linear-gradient(135deg, var(--primary-gold), var(--accent-orange));
                border-radius: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 2.5rem;
                font-weight: 800;
                color: white;
                box-shadow: 0 8px 32px rgba(244, 196, 48, 0.3);
            }
            
            .landing-title {
                font-size: 4rem;
                font-weight: 800;
                color: var(--primary-gold);
                margin: 2rem 0 1rem 0;
                text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .landing-subtitle {
                font-size: 1.2rem;
                color: var(--text-secondary);
                max-width: 600px;
                margin: 0 auto 3rem auto;
                line-height: 1.6;
            }
            
            .cta-buttons {
                display: flex;
                gap: 1rem;
                justify-content: center;
                flex-wrap: wrap;
                margin-bottom: 4rem;
            }
            
            .btn-primary-gold {
                background: linear-gradient(135deg, var(--primary-gold), var(--accent-orange));
                color: white;
                padding: 16px 32px;
                border-radius: 12px;
                border: none;
                font-weight: 600;
                font-size: 1.1rem;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 20px rgba(244, 196, 48, 0.3);
            }
            
            .btn-primary-gold:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 32px rgba(244, 196, 48, 0.4);
            }
            
            .btn-outline-gold {
                background: transparent;
                color: var(--primary-gold);
                padding: 16px 32px;
                border: 2px solid var(--primary-gold);
                border-radius: 12px;
                font-weight: 600;
                font-size: 1.1rem;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .btn-outline-gold:hover {
                background: var(--primary-gold);
                color: white;
            }
            
            .features-section {
                padding: 80px 20px;
                background: white;
            }
            
            .section-title {
                font-size: 2.5rem;
                font-weight: 700;
                text-align: center;
                margin-bottom: 3rem;
                color: var(--text-primary);
            }
            
            .text-gold {
                color: var(--primary-gold);
            }
            
            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 2rem;
                max-width: 1000px;
                margin: 0 auto;
            }
            
            .feature-card {
                background: white;
                padding: 2rem;
                border-radius: 16px;
                text-align: center;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                transition: all 0.3s ease;
                border: 1px solid #f0f0f0;
            }
            
            .feature-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 12px 40px rgba(0,0,0,0.12);
            }
            
            .feature-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
            }
            
            .feature-card h3 {
                font-size: 1.3rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
                color: var(--text-primary);
            }
            
            .feature-card p {
                color: var(--text-secondary);
                line-height: 1.5;
            }
            
            .cta-section {
                padding: 80px 20px;
                background: linear-gradient(135deg, #f5f5f7 0%, #f8f9fa 100%);
                text-align: center;
            }
            
            .cta-title {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 1rem;
                color: var(--text-primary);
            }
            
            .cta-subtitle {
                font-size: 1.1rem;
                color: var(--text-secondary);
                max-width: 600px;
                margin: 0 auto 2rem auto;
                line-height: 1.6;
            }
            
            .hidden {
                display: none;
            }
            
            .page {
                animation: fadeIn 0.5s ease-in-out;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            /* Dark theme for subjects page */
            .dark-theme {
                background: var(--dark-bg);
                color: var(--dark-text-primary);
                min-height: 100vh;
            }
            
            .subjects-header {
                text-align: center;
                padding: 3rem 2rem;
            }
            
            .subjects-title {
                font-size: 2.5rem;
                font-weight: 700;
                color: var(--dark-text-primary);
                margin-bottom: 1rem;
            }
            
            .subjects-subtitle {
                color: var(--dark-text-secondary);
                font-size: 1.1rem;
                max-width: 600px;
                margin: 0 auto;
            }
            
            .subjects-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 2rem;
                max-width: 1000px;
                margin: 0 auto;
                padding: 0 2rem;
            }
            
            .subject-card {
                background: var(--dark-card);
                border-radius: 16px;
                padding: 2rem;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                border: 1px solid var(--dark-border);
                position: relative;
                overflow: hidden;
            }
            
            .subject-card:hover {
                transform: translateY(-4px);
                box-shadow: 0 12px 40px rgba(0,0,0,0.3);
            }
            
            .subject-icon {
                font-size: 3rem;
                margin-bottom: 1rem;
            }
            
            .subject-name {
                font-size: 1.5rem;
                font-weight: 600;
                color: var(--dark-text-primary);
                margin-bottom: 0.5rem;
            }
            
            .subject-desc {
                color: var(--dark-text-secondary);
                line-height: 1.5;
            }
            
            @media (max-width: 768px) {
                .landing-title {
                    font-size: 2.5rem;
                }
                
                .features-grid,
                .subjects-grid {
                    grid-template-columns: 1fr;
                }
                
                .cta-buttons {
                    flex-direction: column;
                    align-items: center;
                }
                
                .btn-primary-gold,
                .btn-outline-gold {
                    width: 100%;
                    max-width: 300px;
                }
            }
        </style>
    </head>
    <body>
        <div id="app" class="app-container">
            <div id="landing" class="page">
                <div class="landing-hero">
                    <div class="brand-logo">
                        <div class="crown-icon">👑</div>
                        <div class="brand-letter">E</div>
                    </div>
                    
                    <h1 class="landing-title">EduLLM</h1>
                    
                    <p class="landing-subtitle">
                        Your AI-powered homework companion. Get instant, accurate answers
                        to your school questions using cutting-edge Large Language Model
                        technology.
                    </p>
                    
                    <div class="cta-buttons">
                        <button class="btn-primary-gold" onclick="showLogin()">Start Learning</button>
                        <button class="btn-outline-gold" onclick="showFeatures()">Learn More</button>
                    </div>
                </div>

                <div class="features-section">
                    <h2 class="section-title">Why Choose <span class="text-gold">EduLLM?</span></h2>
                    
                    <div class="features-grid">
                        <div class="feature-card">
                            <div class="feature-icon">🧠</div>
                            <h3>AI-Powered Learning</h3>
                            <p>Advanced LLM technology helps you understand complex concepts with personalized explanations.</p>
                        </div>
                        
                        <div class="feature-card">
                            <div class="feature-icon">📖</div>
                            <h3>Multiple Subjects</h3>
                            <p>Get help with Math, Science, History, English, and more - all in one platform.</p>
                        </div>
                        
                        <div class="feature-card">
                            <div class="feature-icon">💡</div>
                            <h3>Instant Solutions</h3>
                            <p>Get step-by-step solutions to your homework problems in seconds.</p>
                        </div>
                        
                        <div class="feature-card">
                            <div class="feature-icon">👥</div>
                            <h3>Student Community</h3>
                            <p>Join thousands of students who are already improving their grades with EduLLM.</p>
                        </div>
                    </div>
                </div>

                <div class="cta-section">
                    <h2 class="cta-title">Ready to Ace Your Homework?</h2>
                    <p class="cta-subtitle">
                        Join thousands of students who are already using EduLLM to improve their
                        understanding and grades.
                    </p>
                    <button class="btn-primary-gold" onclick="showLogin()">Get Started Today</button>
                </div>
            </div>
            
            <div id="subjects" class="page dark-theme hidden">
                <div class="subjects-header">
                    <h1 class="subjects-title">
                        Choose Your <span class="text-gold">Subject</span>
                    </h1>
                    <p class="subjects-subtitle">
                        Select a subject to get started with your homework questions. Our AI tutor
                        is ready to help!
                    </p>
                </div>
                
                <div class="subjects-grid">
                    <div class="subject-card" onclick="showQuestion('Mathematics')">
                        <div class="subject-icon">📐</div>
                        <h3 class="subject-name">Mathematics</h3>
                        <p class="subject-desc">Algebra, Calculus, Geometry, Statistics</p>
                    </div>
                    
                    <div class="subject-card" onclick="showQuestion('Chemistry')">
                        <div class="subject-icon">🧪</div>
                        <h3 class="subject-name">Chemistry</h3>
                        <p class="subject-desc">Organic, Inorganic, Physical Chemistry</p>
                    </div>
                    
                    <div class="subject-card" onclick="showQuestion('History')">
                        <div class="subject-icon">🏛️</div>
                        <h3 class="subject-name">History</h3>
                        <p class="subject-desc">World History, Ancient Civilizations</p>
                    </div>
                    
                    <div class="subject-card" onclick="showQuestion('English')">
                        <div class="subject-icon">📚</div>
                        <h3 class="subject-name">English</h3>
                        <p class="subject-desc">Literature, Grammar, Writing</p>
                    </div>
                    
                    <div class="subject-card" onclick="showQuestion('Biology')">
                        <div class="subject-icon">🧬</div>
                        <h3 class="subject-name">Biology</h3>
                        <p class="subject-desc">Cell Biology, Genetics, Ecology</p>
                    </div>
                    
                    <div class="subject-card" onclick="showQuestion('Economics')">
                        <div class="subject-icon">💰</div>
                        <h3 class="subject-name">Economics</h3>
                        <p class="subject-desc">Micro, Macro, International Economics</p>
                    </div>
                </div>
                
                <div style="text-align: center; padding: 2rem;">
                    <button class="btn-outline-gold" onclick="showLanding()">← Back to Home</button>
                </div>
            </div>
        </div>

        <script>
            function showPage(pageId) {
                // Hide all pages
                document.querySelectorAll('.page').forEach(page => {
                    page.classList.add('hidden');
                });
                
                // Show selected page
                const page = document.getElementById(pageId);
                if (page) {
                    page.classList.remove('hidden');
                }
            }
            
            function showLanding() {
                showPage('landing');
            }
            
            function showLogin() {
                // For now, skip login and go directly to subjects
                showSubjects();
            }
            
            function showSubjects() {
                showPage('subjects');
            }
            
            function showQuestion(subject) {
                alert(`Coming soon: ${subject} questions!\\n\\nThis will connect to your Streamlit backend for actual question processing.`);
            }
            
            function showFeatures() {
                document.querySelector('.features-section').scrollIntoView({
                    behavior: 'smooth'
                });
            }
        </script>
    </body>
    </html>
    """
    
    # Display the frontend
    components.html(frontend_html, height=1000, scrolling=True)

if __name__ == '__main__':
    main()
