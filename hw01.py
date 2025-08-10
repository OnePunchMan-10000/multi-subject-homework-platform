import streamlit as st
import requests
import json
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import re

# Page configuration
st.set_page_config(
    page_title="Academic Assistant Pro",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for clean, modern UI
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom styling */
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    /* Fix visibility issues */
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    
    .subject-card {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        color: white;
    }
    
    .answer-container {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        color: white;
    }
    
    .step-box {
        background: rgba(76, 175, 80, 0.1);
        border-left: 4px solid #4CAF50;
        padding: 12px;
        margin: 8px 0;
        border-radius: 4px;
        color: white;
    }
    
    .formula-box {
        background: rgba(255, 193, 7, 0.1);
        border: 1px solid #ffc107;
        padding: 10px;
        border-radius: 4px;
        text-align: center;
        font-family: 'Courier New', monospace;
        margin: 10px 0;
        color: #ffc107;
    }
    
    .stSelectbox > div > div {
        background-color: rgba(255,255,255,0.1);
        color: white;
    }
    
    .stTextArea textarea {
        background-color: rgba(255,255,255,0.1) !important;
        border: 2px solid rgba(255,255,255,0.2) !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    /* Fix text visibility */
    .stSelectbox label, .stTextArea label {
        color: white !important;
    }
    
    .stMarkdown, .stText {
        color: white;
    }
    
    /* Fix dropdown text */
    .stSelectbox > div > div > div {
        color: white;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced subject configurations with refined prompts
SUBJECTS = {
    "Mathematics": {
        "icon": "📐",
        "prompt": """You are an expert mathematics tutor with PhD-level knowledge. Provide step-by-step solutions that are:
- Mathematically rigorous and textbook-accurate
- Clearly explained with proper mathematical notation
- Include all intermediate steps
- Show work verification
- Use proper mathematical terminology
- Format equations clearly using standard notation""",
        "example": "Solve: 3x² - 12x + 9 = 0"
    },
    "Physics": {
        "icon": "⚡",
        "prompt": """You are a physics professor with expertise in all physics domains. Provide solutions that:
- Use correct physics principles and formulas
- Show dimensional analysis where applicable
- Include proper units throughout calculations
- Explain the physics concepts involved
- Draw connections to real-world applications
- Follow standard physics problem-solving methodology""",
        "example": "A 2kg object falls from 10m height. Find velocity just before impact."
    },
    "Chemistry": {
        "icon": "🧪",
        "prompt": """You are a chemistry expert with advanced knowledge. Provide solutions that:
- Use accurate chemical formulas and equations
- Balance chemical equations properly
- Include proper chemical nomenclature
- Show stoichiometric calculations step-by-step
- Explain molecular behavior and mechanisms
- Use standard chemistry notation and units""",
        "example": "Balance: Al + O₂ → Al₂O₃"
    },
    "Biology": {
        "icon": "🧬",
        "prompt": """You are a biology expert with comprehensive knowledge. Provide explanations that:
- Use accurate biological terminology
- Explain biological processes clearly
- Include relevant examples and analogies
- Connect concepts to real biological systems
- Use proper scientific classification
- Reference current biological understanding""",
        "example": "Explain the process of cellular respiration in detail."
    },
    "English Literature": {
        "icon": "📚",
        "prompt": """You are an English literature scholar with deep analytical skills. Provide analysis that:
- Uses proper literary terminology and concepts
- Includes textual evidence and citations
- Analyzes themes, symbols, and literary devices
- Considers historical and cultural context
- Follows academic writing standards
- Provides insightful interpretations""",
        "example": "Analyze the symbolism of light and darkness in Romeo and Juliet."
    },
    "History": {
        "icon": "🏛️",
        "prompt": """You are a history professor with expertise across time periods. Provide analysis that:
- Uses accurate historical facts and dates
- Considers multiple perspectives and sources
- Analyzes cause-and-effect relationships
- Includes relevant historical context
- Uses proper historical methodology
- Maintains objectivity while explaining significance""",
        "example": "Analyze the causes of World War I."
    },
    "Economics": {
        "icon": "💰",
        "prompt": """You are an economics expert with theoretical and practical knowledge. Provide explanations that:
- Use correct economic terminology and principles
- Include relevant graphs and models where applicable
- Explain both micro and macroeconomic concepts
- Use real-world examples and applications
- Show mathematical calculations for economic problems
- Connect theory to current economic conditions""",
        "example": "Explain supply and demand equilibrium with a market example."
    },
    "Computer Science": {
        "icon": "💻",
        "prompt": """You are a computer science expert with programming and theoretical knowledge. Provide solutions that:
- Use correct programming syntax and best practices
- Explain algorithms clearly with complexity analysis
- Include working code examples when relevant
- Explain computer science concepts thoroughly
- Use proper technical terminology
- Consider efficiency and optimization""",
        "example": "Implement binary search algorithm in Python."
    }
}

def get_api_response(question, subject):
    """Get response from OpenRouter API with enhanced prompting"""
    
    # Check if API key exists
    if 'OPENROUTER_API_KEY' not in st.secrets:
        st.error("⚠️ API key not configured. Please add OPENROUTER_API_KEY to Streamlit secrets.")
        return None
    
    api_key = st.secrets['OPENROUTER_API_KEY']
    
    # Enhanced system prompt - more detailed for better answers
    system_prompt = f"""
    You are an expert {subject} tutor providing comprehensive, step-by-step solutions.
    
    CRITICAL REQUIREMENTS:
    1. Provide DETAILED explanations with multiple steps
    2. Show ALL mathematical work and intermediate calculations
    3. Use clear mathematical notation (write fractions as 3/2, exponents as x^2, square roots as sqrt())
    4. Explain WHY each step is taken
    5. Include verification/checking of the final answer
    6. For math problems: show the formula first, then substitute values, then calculate
    7. Break complex problems into smaller, manageable steps
    8. Be thorough and educational - students should understand the process completely
    
    FORMATTING:
    - Use "Step 1:", "Step 2:", etc. for clear organization
    - Put final answers in a separate "Final Answer:" section
    - Use simple text formatting (no LaTeX symbols like \\frac or \\sqrt)
    - Write equations clearly: x = (-b ± sqrt(b^2 - 4ac)) / (2a)
    
    Subject: {subject}
    """
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "openai/gpt-3.5-turbo",  # Cheaper model to save credits
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        "temperature": 0.1,
        "max_tokens": 1200  # Increased for more detailed responses
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Network Error: {str(e)}")
        return None

def create_advanced_visualization(question, subject):
    """Create subject-specific visualizations and diagrams"""
    question_lower = question.lower()
    
    try:
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if subject == "Mathematics":
            # Quadratic functions
            if any(term in question_lower for term in ['x²', 'x^2', 'quadratic', 'parabola']):
                x = np.linspace(-10, 10, 400)
                y = x**2
                ax.plot(x, y, 'b-', linewidth=2, label='y = x²')
                ax.grid(True, alpha=0.3)
                ax.axhline(y=0, color='k', linewidth=0.5)
                ax.axvline(x=0, color='k', linewidth=0.5)
                ax.set_xlabel('x', fontsize=12)
                ax.set_ylabel('y', fontsize=12)
                ax.set_title('Quadratic Function', fontsize=14, fontweight='bold')
                ax.legend(fontsize=11)
                
            # Linear equations
            elif any(term in question_lower for term in ['linear', 'y=', 'slope']):
                x = np.linspace(-10, 10, 100)
                y = 2*x + 3  # Example linear function
                ax.plot(x, y, 'r-', linewidth=2, label='y = 2x + 3')
                ax.grid(True, alpha=0.3)
                ax.axhline(y=0, color='k', linewidth=0.5)
                ax.axvline(x=0, color='k', linewidth=0.5)
                ax.set_xlabel('x', fontsize=12)
                ax.set_ylabel('y', fontsize=12)
                ax.set_title('Linear Function', fontsize=14, fontweight='bold')
                ax.legend(fontsize=11)
                
            # Trigonometric functions
            elif any(term in question_lower for term in ['sin', 'cos', 'tan', 'trigonometric']):
                x = np.linspace(-2*np.pi, 2*np.pi, 400)
                y1 = np.sin(x)
                y2 = np.cos(x)
                ax.plot(x, y1, 'b-', linewidth=2, label='sin(x)')
                ax.plot(x, y2, 'r-', linewidth=2, label='cos(x)')
                ax.grid(True, alpha=0.3)
                ax.axhline(y=0, color='k', linewidth=0.5)
                ax.axvline(x=0, color='k', linewidth=0.5)
                ax.set_xlabel('x (radians)', fontsize=12)
                ax.set_ylabel('y', fontsize=12)
                ax.set_title('Trigonometric Functions', fontsize=14, fontweight='bold')
                ax.legend(fontsize=11)
                
            # Circle/geometry
            elif any(term in question_lower for term in ['circle', 'radius', 'circumference']):
                theta = np.linspace(0, 2*np.pi, 100)
                r = 5  # radius
                x = r * np.cos(theta)
                y = r * np.sin(theta)
                ax.plot(x, y, 'b-', linewidth=2, label=f'Circle (r={r})')
                ax.set_aspect('equal')
                ax.grid(True, alpha=0.3)
                ax.axhline(y=0, color='k', linewidth=0.5)
                ax.axvline(x=0, color='k', linewidth=0.5)
                ax.set_xlabel('x', fontsize=12)
                ax.set_ylabel('y', fontsize=12)
                ax.set_title('Circle', fontsize=14, fontweight='bold')
                ax.legend(fontsize=11)
                
        elif subject == "Physics":
            # Motion graphs
            if any(term in question_lower for term in ['motion', 'velocity', 'acceleration', 'displacement']):
                t = np.linspace(0, 10, 100)
                # Example: uniformly accelerated motion
                v = 5 + 2*t  # v = u + at
                s = 5*t + t**2  # s = ut + 0.5*at²
                
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
                
                ax1.plot(t, v, 'r-', linewidth=2, label='Velocity')
                ax1.set_xlabel('Time (s)', fontsize=12)
                ax1.set_ylabel('Velocity (m/s)', fontsize=12)
                ax1.set_title('Velocity vs Time', fontsize=14, fontweight='bold')
                ax1.grid(True, alpha=0.3)
                ax1.legend(fontsize=11)
                
                ax2.plot(t, s, 'b-', linewidth=2, label='Displacement')
                ax2.set_xlabel('Time (s)', fontsize=12)
                ax2.set_ylabel('Displacement (m)', fontsize=12)
                ax2.set_title('Displacement vs Time', fontsize=14, fontweight='bold')
                ax2.grid(True, alpha=0.3)
                ax2.legend(fontsize=11)
                
                plt.tight_layout()
                
            # Wave functions
            elif any(term in question_lower for term in ['wave', 'frequency', 'amplitude']):
                x = np.linspace(0, 4*np.pi, 400)
                y = 2 * np.sin(x)  # Amplitude = 2
                ax.plot(x, y, 'g-', linewidth=2, label='Wave function')
                ax.grid(True, alpha=0.3)
                ax.axhline(y=0, color='k', linewidth=0.5)
                ax.set_xlabel('Distance (m)', fontsize=12)
                ax.set_ylabel('Amplitude', fontsize=12)
                ax.set_title('Wave Function', fontsize=14, fontweight='bold')
                ax.legend(fontsize=11)
                
        elif subject == "Chemistry":
            # Molecular structures (simplified)
            if any(term in question_lower for term in ['molecule', 'bond', 'structure']):
                # Simple molecule representation
                ax.scatter([0, 1, 2], [0, 1, 0], s=200, c=['red', 'blue', 'red'], alpha=0.7)
                ax.plot([0, 1, 2], [0, 1, 0], 'k-', linewidth=2)
                ax.text(0, -0.2, 'O', ha='center', fontsize=14, fontweight='bold')
                ax.text(1, 1.2, 'C', ha='center', fontsize=14, fontweight='bold')
                ax.text(2, -0.2, 'O', ha='center', fontsize=14, fontweight='bold')
                ax.set_title('Molecular Structure Example', fontsize=14, fontweight='bold')
                ax.set_xlim(-0.5, 2.5)
                ax.set_ylim(-0.5, 1.5)
                ax.set_aspect('equal')
                ax.grid(True, alpha=0.3)
                
        # If no specific visualization created, return None
        else:
            plt.close(fig)
            return None
            
        # Save plot to bytes
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=150, facecolor='white')
        buf.seek(0)
        plt.close(fig)
        
        return buf
        
    except Exception as e:
        plt.close('all')
        return None

def format_math_response(response_text):
    """Format mathematical responses with proper styling and symbol conversion"""
    formatted = response_text
    
    # Convert common mathematical expressions to readable format
    formatted = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1/\2', formatted)
    formatted = re.sub(r'\\sqrt\{([^}]+)\}', r'sqrt(\1)', formatted)
    formatted = re.sub(r'\\\(([^)]+)\\\)', r'\1', formatted)
    formatted = re.sub(r'\\\[([^\]]+)\\\]', r'\1', formatted)
    
    # Highlight equations and steps
    lines = formatted.split('\n')
    processed_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            processed_lines.append('<br>')
            continue
            
        # Format step headers
        if re.match(r'^Step \d+:', line):
            processed_lines.append(f'<div class="step-box"><strong>{line}</strong></div>')
        
        # Format equations (lines with = sign)
        elif '=' in line and any(char in line for char in ['x', '+', '-', '*', '/', '^', 'sqrt']):
            processed_lines.append(f'<div class="math-step">{line}</div>')
        
        # Format final answer
        elif line.startswith('Final Answer:') or line.startswith('Therefore'):
            processed_lines.append(f'<div class="formula-box">{line}</div>')
        
        # Regular text
        else:
            processed_lines.append(f'<p>{line}</p>')
    
    return ''.join(processed_lines)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎓 Academic Assistant Pro</h1>
        <p>Expert-level homework assistance across all subjects</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main interface
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📖 Select Subject")
        
        # Subject selection with icons
        subject_options = [f"{info['icon']} {subject}" for subject, info in SUBJECTS.items()]
        selected_subject_display = st.selectbox(
            "Choose your subject:",
            subject_options,
            help="Select the academic subject for your question"
        )
        
        # Extract actual subject name
        selected_subject = selected_subject_display.split(' ', 1)[1]
        
        # Show example question
        st.markdown("### 💡 Example Question")
        with st.expander("See example"):
            st.info(f"**{selected_subject}**: {SUBJECTS[selected_subject]['example']}")
    
    with col2:
        st.markdown("### ❓ Your Question")
        
        # Question input
        question = st.text_area(
            "Enter your homework question:",
            height=120,
            placeholder=f"Ask your {selected_subject} question here...",
            help="Be specific and include all relevant details"
        )
        
        # Solve button
        if st.button("🎯 Get Solution", type="primary"):
            if question.strip():
                with st.spinner(f"Analyzing your {selected_subject} question..."):
                    # Get AI response
                    response = get_api_response(question, selected_subject)
                    
                    if response:
                        # Display clean answer
                        st.markdown("### 📝 Solution")
                        
                        # Format response based on subject
                        if selected_subject == "Mathematics":
                            formatted_response = format_math_response(response)
                        else:
                            formatted_response = response.replace('\n\n', '<br><br>')
                        
                        with st.container():
                            st.markdown(f"""
                            <div class="answer-container">
                                <h4>{SUBJECTS[selected_subject]['icon']} {selected_subject} Solution</h4>
                                <div>
                                    {formatted_response}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Add visualizations for applicable subjects
                        if selected_subject in ["Mathematics", "Physics", "Chemistry"]:
                            with st.spinner("Creating visualization..."):
                                viz = create_advanced_visualization(question, selected_subject)
                                if viz:
                                    st.markdown("### 📊 Visual Representation")
                                    st.image(viz, use_column_width=True, caption=f"{selected_subject} Visualization")
                                    st.markdown('<div style="margin-bottom: 20px;"></div>', unsafe_allow_html=True)
                        
                        # Feedback section
                        st.markdown("### 📊 Rate this solution")
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            if st.button("👍 Helpful"):
                                st.success("Thank you for your feedback!")
                        with col_b:
                            if st.button("👎 Needs improvement"):
                                st.info("We'll work on improving our responses!")
                        with col_c:
                            if st.button("🔄 Try again"):
                                st.rerun()
                    
            else:
                st.warning("⚠️ Please enter a question to get help.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🎓 Academic Assistant Pro - Powered by Advanced AI</p>
        <p><small>Providing accurate, textbook-quality educational assistance</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
