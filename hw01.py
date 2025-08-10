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

# Custom CSS for clean, modern UI with improved spacing
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom styling */
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Fix visibility issues */
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    
    /* Solution container with proper spacing */
    .solution-container {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        border: 2px solid #4CAF50;
        border-radius: 12px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.15);
    }
    
    /* Step headers with consistent styling */
    .step-header {
        background: linear-gradient(90deg, #4CAF50, #45a049);
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        margin: 25px 0 15px 0;
        font-size: 1.2em;
        font-weight: bold;
        box-shadow: 0 3px 10px rgba(76, 175, 80, 0.3);
    }
    
    /* Mathematical expressions */
    .math-expression {
        background: rgba(255, 193, 7, 0.15);
        border: 2px solid #ffc107;
        border-radius: 8px;
        padding: 20px;
        margin: 20px 0;
        font-family: 'Courier New', monospace;
        font-size: 1.3em;
        text-align: center;
        color: #ffc107;
        line-height: 1.8;
        box-shadow: 0 3px 10px rgba(255, 193, 7, 0.2);
    }
    
    /* Final answer highlighting */
    .final-answer {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        color: white;
        border-radius: 12px;
        padding: 25px;
        margin: 30px 0;
        text-align: center;
        font-size: 1.4em;
        font-weight: bold;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
        border: 3px solid #66bb6a;
    }
    
    /* Regular text with proper spacing */
    .explanation-text {
        color: #e0e0e0;
        font-size: 1.1em;
        line-height: 1.7;
        margin: 15px 0;
        padding: 0 10px;
    }
    
    /* Formula box */
    .formula-box {
        background: rgba(156, 39, 176, 0.15);
        border: 2px solid #9C27B0;
        border-radius: 8px;
        padding: 20px;
        margin: 20px 0;
        font-family: 'Courier New', monospace;
        font-size: 1.2em;
        text-align: center;
        color: #CE93D8;
        line-height: 1.6;
        box-shadow: 0 3px 10px rgba(156, 39, 176, 0.2);
    }
    
    /* Fraction styling */
    .fraction {
        display: inline-block;
        text-align: center;
        vertical-align: middle;
        margin: 0 5px;
    }
    
    .fraction-numerator {
        border-bottom: 2px solid #ffc107;
        padding-bottom: 2px;
        display: block;
    }
    
    .fraction-denominator {
        padding-top: 2px;
        display: block;
    }
    
    /* Input styling */
    .stTextArea textarea {
        background-color: rgba(255,255,255,0.1) !important;
        border: 2px solid rgba(255,255,255,0.3) !important;
        border-radius: 8px !important;
        color: white !important;
        font-size: 1.1em !important;
    }
    
    .stSelectbox > div > div {
        background-color: rgba(255,255,255,0.1);
        color: white;
        border-radius: 8px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 2rem;
        font-weight: 600;
        font-size: 1.1em;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Labels */
    .stSelectbox label, .stTextArea label {
        color: white !important;
        font-weight: 600 !important;
        font-size: 1.1em !important;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced subject configurations
SUBJECTS = {
    "Mathematics": {
        "icon": "📐",
        "prompt": """You are an expert mathematics tutor with PhD-level knowledge. Provide step-by-step solutions that are:
- Mathematically rigorous and textbook-accurate
- Clearly explained with proper mathematical notation
- Include all intermediate steps with clear explanations
- Show work verification when applicable
- Use proper mathematical terminology
- Format equations clearly using standard notation

CRITICAL FORMATTING REQUIREMENTS:
1. Start each step with "**Step X:**" followed by a clear description
2. Put mathematical expressions on separate lines
3. Use simple notation: fractions as a/b, exponents as x^2, square roots as sqrt(x)
4. End with "**Final Answer:**" in bold
5. Include a brief verification when possible
6. Use clear spacing between steps""",
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
- Follow standard physics problem-solving methodology

Format with clear steps, mathematical expressions on separate lines, and bold headers.""",
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
- Use standard chemistry notation and units

Format with clear step headers and proper spacing between calculations.""",
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
- Reference current biological understanding

Format with clear section headers and well-organized explanations.""",
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
- Provides insightful interpretations

Format with clear analytical sections and supporting evidence.""",
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
- Maintains objectivity while explaining significance

Format with chronological or thematic organization and clear explanations.""",
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
- Connect theory to current economic conditions

Format with clear economic analysis and step-by-step calculations.""",
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
- Consider efficiency and optimization

Format with clear code blocks and step-by-step explanations.""",
        "example": "Implement binary search algorithm in Python."
    }
}

def should_show_diagram(question, subject):
    """Improved diagram detection"""
    question_lower = question.lower()
    
    # Strong visual indicators
    strong_visual_keywords = [
        'draw', 'sketch', 'plot', 'graph', 'construct', 'visualize', 
        'diagram', 'figure', 'chart', 'show graphically', 'illustrate',
        'represent visually', 'create diagram', 'make chart', 'display'
    ]
    
    for keyword in strong_visual_keywords:
        if keyword in question_lower:
            return True
    
    # Subject-specific visual keywords
    subject_keywords = {
        'Mathematics': [
            'parabola', 'quadratic', 'function', 'linear', 'curve', 'slope',
            'triangle', 'circle', 'rectangle', 'angle', 'coordinate',
            'sin', 'cos', 'tan', 'trigonometric', 'x²', 'x^2', 'y='
        ],
        'Physics': [
            'wave', 'frequency', 'amplitude', 'projectile', 'trajectory', 
            'motion', 'force diagram', 'circuit', 'field', 'vector'
        ],
        'Chemistry': [
            'reaction rate', 'concentration', 'molecular structure', 
            'lewis structure', 'phase diagram', 'orbital'
        ],
        'Biology': [
            'population growth', 'cell cycle', 'dna structure', 'ecosystem',
            'life cycle', 'growth curve', 'distribution'
        ],
        'Economics': [
            'supply', 'demand', 'curve', 'equilibrium', 'market',
            'production possibilities', 'cost curve'
        ]
    }
    
    if subject in subject_keywords:
        for keyword in subject_keywords[subject]:
            if keyword in question_lower:
                return True
    
    return False

def create_smart_visualization(question, subject):
    """Create intelligent visualizations"""
    question_lower = question.lower()
    
    try:
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        
        if subject == "Mathematics":
            if any(term in question_lower for term in ['x²', 'x^2', 'quadratic', 'parabola']):
                x = np.linspace(-10, 10, 400)
                y = x**2
                ax.plot(x, y, 'b-', linewidth=3, label='y = x²')
                ax.grid(True, alpha=0.3)
                ax.axhline(y=0, color='k', linewidth=0.8)
                ax.axvline(x=0, color='k', linewidth=0.8)
                ax.set_xlabel('x', fontsize=14, fontweight='bold')
                ax.set_ylabel('y', fontsize=14, fontweight='bold')
                ax.set_title('Quadratic Function', fontsize=16, fontweight='bold')
                ax.legend(fontsize=12)
                
            elif any(term in question_lower for term in ['linear', 'y=', 'slope', 'line']) and 'x' in question_lower:
                x = np.linspace(-10, 10, 100)
                y = 2*x + 3
                ax.plot(x, y, 'r-', linewidth=3, label='y = 2x + 3')
                ax.grid(True, alpha=0.3)
                ax.axhline(y=0, color='k', linewidth=0.8)
                ax.axvline(x=0, color='k', linewidth=0.8)
                ax.set_xlabel('x', fontsize=14, fontweight='bold')
                ax.set_ylabel('y', fontsize=14, fontweight='bold')
                ax.set_title('Linear Function', fontsize=16, fontweight='bold')
                ax.legend(fontsize=12)
                
            elif any(term in question_lower for term in ['sin', 'cos', 'trigonometric']):
                x = np.linspace(-2*np.pi, 2*np.pi, 400)
                y1 = np.sin(x)
                y2 = np.cos(x)
                ax.plot(x, y1, 'b-', linewidth=3, label='sin(x)')
                ax.plot(x, y2, 'r-', linewidth=3, label='cos(x)')
                ax.grid(True, alpha=0.3)
                ax.axhline(y=0, color='k', linewidth=0.8)
                ax.axvline(x=0, color='k', linewidth=0.8)
                ax.set_xlabel('x (radians)', fontsize=14, fontweight='bold')
                ax.set_ylabel('y', fontsize=14, fontweight='bold')
                ax.set_title('Trigonometric Functions', fontsize=16, fontweight='bold')
                ax.legend(fontsize=12)
                
            else:
                x = np.linspace(-5, 5, 100)
                y = x**2 - 4
                ax.plot(x, y, 'b-', linewidth=3, label='y = x² - 4')
                ax.grid(True, alpha=0.3)
                ax.axhline(y=0, color='k', linewidth=0.8)
                ax.axvline(x=0, color='k', linewidth=0.8)
                ax.set_xlabel('x', fontsize=14, fontweight='bold')
                ax.set_ylabel('y', fontsize=14, fontweight='bold')
                ax.set_title('Mathematical Function', fontsize=16, fontweight='bold')
                ax.legend(fontsize=12)
        
        elif subject == "Physics":
            if any(term in question_lower for term in ['wave', 'frequency', 'amplitude']):
                t = np.linspace(0, 4*np.pi, 400)
                y = np.sin(t)
                ax.plot(t, y, 'b-', linewidth=3, label='Wave Function')
                ax.grid(True, alpha=0.3)
                ax.set_xlabel('Time/Position', fontsize=14, fontweight='bold')
                ax.set_ylabel('Amplitude', fontsize=14, fontweight='bold')
                ax.set_title('Wave Pattern', fontsize=16, fontweight='bold')
                ax.legend(fontsize=12)
            else:
                t = np.linspace(0, 2*np.pi, 100)
                y = np.sin(t)
                ax.plot(t, y, 'g-', linewidth=3, label='Physics Function')
                ax.grid(True, alpha=0.3)
                ax.set_xlabel('Parameter', fontsize=14, fontweight='bold')
                ax.set_ylabel('Value', fontsize=14, fontweight='bold')
                ax.set_title('Physics Visualization', fontsize=16, fontweight='bold')
                ax.legend(fontsize=12)
        
        elif subject == "Economics":
            quantity = np.linspace(0, 10, 100)
            supply = 2 * quantity
            demand = 20 - quantity
            ax.plot(quantity, supply, 'b-', linewidth=3, label='Supply')
            ax.plot(quantity, demand, 'r-', linewidth=3, label='Demand')
            
            eq_quantity = 20/3
            eq_price = 2 * eq_quantity
            ax.plot(eq_quantity, eq_price, 'go', markersize=10, label='Equilibrium')
            
            ax.grid(True, alpha=0.3)
            ax.set_xlabel('Quantity', fontsize=14, fontweight='bold')
            ax.set_ylabel('Price', fontsize=14, fontweight='bold')
            ax.set_title('Supply and Demand', fontsize=16, fontweight='bold')
            ax.legend(fontsize=12)
        
        else:
            x = np.linspace(-5, 5, 100)
            y = np.sin(x)
            ax.plot(x, y, 'purple', linewidth=3, label='Function')
            ax.grid(True, alpha=0.3)
            ax.set_xlabel('X', fontsize=14, fontweight='bold')
            ax.set_ylabel('Y', fontsize=14, fontweight='bold')
            ax.set_title(f'{subject} Visualization', fontsize=16, fontweight='bold')
            ax.legend(fontsize=12)
        
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=150, facecolor='white')
        buf.seek(0)
        plt.close(fig)
        return buf
        
    except Exception as e:
        plt.close('all')
        return None

def get_api_response(question, subject):
    """Get response from OpenRouter API"""
    if 'OPENROUTER_API_KEY' not in st.secrets:
        st.error("⚠️ API key not configured. Please add OPENROUTER_API_KEY to Streamlit secrets.")
        return None
    
    api_key = st.secrets['OPENROUTER_API_KEY']
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SUBJECTS[subject]['prompt']},
            {"role": "user", "content": question}
        ],
        "temperature": 0.1,
        "max_tokens": 2000
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
            st.error(f"API Error: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        st.error(f"Network Error: {str(e)}")
        return None

def format_solution_response(response_text):
    """Format solution with consistent spacing and styling"""
    if not response_text:
        return ""
    
    # Clean up the response
    lines = response_text.strip().split('\n')
    formatted_html = []
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines but add spacing
        if not line:
            formatted_html.append('<div style="height: 15px;"></div>')
            continue
        
        # Step headers
        if re.match(r'^\*\*Step \d+:', line) or re.match(r'^Step \d+:', line):
            clean_line = re.sub(r'\*\*', '', line)
            formatted_html.append(f'<div class="step-header">{clean_line}</div>')
        
        # Final Answer
        elif line.startswith('**Final Answer') or line.startswith('Final Answer'):
            clean_line = re.sub(r'\*\*', '', line)
            formatted_html.append(f'<div class="final-answer">{clean_line}</div>')
        
        # Mathematical expressions (containing =, +, -, *, /, etc.)
        elif ('=' in line and any(char in line for char in ['x', '+', '-', '*', '/', '^', '(', ')'])) or \
             (any(term in line.lower() for term in ['dx', 'dy', 'sqrt', 'sin', 'cos', 'tan'])):
            formatted_html.append(f'<div class="math-expression">{line}</div>')
        
        # Section headers with **
        elif line.startswith('**') and line.endswith('**'):
            clean_line = line.replace('**', '')
            formatted_html.append(f'<div class="formula-box">{clean_line}</div>')
        
        # Regular explanatory text
        else:
            formatted_html.append(f'<div class="explanation-text">{line}</div>')
    
    return ''.join(formatted_html)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎓 Academic Assistant Pro</h1>
        <p style="font-size: 1.2em; margin-top: 10px;">Expert-level homework assistance with professional formatting</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main interface
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📖 Select Subject")
        
        subject_options = [f"{info['icon']} {subject}" for subject, info in SUBJECTS.items()]
        selected_subject_display = st.selectbox(
            "Choose your subject:",
            subject_options,
            help="Select the academic subject for your question"
        )
        
        selected_subject = selected_subject_display.split(' ', 1)[1]
        
        # Show example
        st.markdown("### 💡 Example Question")
        st.info(f"**{selected_subject}**: {SUBJECTS[selected_subject]['example']}")
    
    with col2:
        st.markdown("### ❓ Your Question")
        
        question = st.text_area(
            "Enter your homework question:",
            height=120,
            placeholder=f"Ask your {selected_subject} question here...",
            help="Be specific and include all relevant details"
        )
        
        if st.button("🎯 Get Solution", type="primary"):
            if question.strip():
                with st.spinner(f"Analyzing your {selected_subject} question..."):
                    response = get_api_response(question, selected_subject)
                    
                    if response:
                        st.markdown("---")
                        st.markdown(f"## 📐 {selected_subject} Solution")
                        
                        # Use the solution container styling
                        formatted_response = format_solution_response(response)
                        st.markdown(f"""
                        <div class="solution-container">
                            {formatted_response}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Check for diagrams
                        if should_show_diagram(question, selected_subject):
                            st.markdown("### 📊 Visual Representation")
                            with st.spinner("Creating visualization..."):
                                viz = create_smart_visualization(question, selected_subject)
                                if viz:
                                    st.image(viz, use_container_width=True, 
                                           caption=f"{selected_subject} Visualization")
                        
                        # Feedback
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
    <div style="text-align: center; color: #888; padding: 2rem;">
        <p style="font-size: 1.1em;">🎓 Academic Assistant Pro - Powered by Advanced AI</p>
        <p><small>Providing accurate, well-formatted educational assistance across all subjects</small></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
