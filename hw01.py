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

# Minimal, clean CSS focusing on readability
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Clean, simple styling */
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    
    .main-header {
        text-align: center;
        padding: 1.5rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    /* Simple, clean text styling */
    .solution-content {
        background-color: rgba(255,255,255,0.05);
        border-left: 4px solid #4CAF50;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    
    .solution-content h3 {
        color: #4CAF50;
        margin: 1.5rem 0 0.5rem 0;
        font-size: 1.2em;
        border-bottom: 2px solid #4CAF50;
        padding-bottom: 0.3rem;
    }
    
    .solution-content p {
        margin: 0.8rem 0;
        line-height: 1.6;
        color: #e0e0e0;
    }
    
    .math-line {
        font-family: 'Courier New', monospace;
        background-color: rgba(255,193,7,0.1);
        padding: 0.5rem;
        margin: 0.5rem 0;
        border-radius: 3px;
        color: #ffc107;
        text-align: center;
    }
    
    .final-answer {
        background-color: rgba(76,175,80,0.2);
        border: 2px solid #4CAF50;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
        font-size: 1.1em;
    }
    
    /* Input styling */
    .stTextArea textarea {
        background-color: rgba(255,255,255,0.1) !important;
        border: 2px solid rgba(255,255,255,0.3) !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    .stSelectbox > div > div {
        background-color: rgba(255,255,255,0.1);
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
    
    .stSelectbox label, .stTextArea label {
        color: white !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced subject configurations with better prompts
SUBJECTS = {
    "Mathematics": {
        "icon": "📐",
        "prompt": """You are an expert mathematics tutor. Provide clear, step-by-step solutions:

FORMATTING REQUIREMENTS:
1. Use "**Step 1:**", "**Step 2:**" etc. for each step
2. Write mathematical expressions in plain text: use x^2 for x², a/b for fractions, sqrt(x) for square roots
3. Put each mathematical equation on its own line
4. Explain the reasoning behind each step
5. End with "**Final Answer:**" 
6. Keep explanations clear and concise
7. Use simple mathematical notation that's easy to read

Provide detailed explanations but keep the formatting clean and readable.""",
        "example": "Solve: 3x² - 12x + 9 = 0"
    },
    "Physics": {
        "icon": "⚡",
        "prompt": """You are a physics expert. Provide clear solutions with:
- Step-by-step approach using "**Step X:**" format
- Clear physics principles and formulas
- Units included in all calculations
- Simple mathematical notation
- Real-world context when helpful""",
        "example": "A 2kg object falls from 10m height. Find velocity just before impact."
    },
    "Chemistry": {
        "icon": "🧪",
        "prompt": """You are a chemistry expert. Provide solutions with:
- Clear step-by-step format
- Proper chemical equations and formulas
- Balanced equations where needed
- Clear explanations of chemical processes
- Simple, readable notation""",
        "example": "Balance: Al + O₂ → Al₂O₃"
    },
    "Biology": {
        "icon": "🧬",
        "prompt": """You are a biology expert. Provide clear explanations with:
- Well-organized structure
- Accurate biological terminology
- Clear examples and analogies
- Step-by-step processes where applicable
- Real-world connections""",
        "example": "Explain the process of cellular respiration in detail."
    },
    "English Literature": {
        "icon": "📚",
        "prompt": """You are an English literature expert. Provide analysis with:
- Clear analytical structure
- Textual evidence and examples
- Literary device explanations
- Historical/cultural context
- Well-organized arguments""",
        "example": "Analyze the symbolism of light and darkness in Romeo and Juliet."
    },
    "History": {
        "icon": "🏛️",
        "prompt": """You are a history expert. Provide analysis with:
- Chronological or thematic organization
- Multiple perspectives and sources
- Cause-and-effect relationships
- Historical context and significance
- Clear, factual explanations""",
        "example": "Analyze the causes of World War I."
    },
    "Economics": {
        "icon": "💰",
        "prompt": """You are an economics expert. Provide explanations with:
- Clear economic principles
- Step-by-step calculations where needed
- Real-world examples
- Simple mathematical notation
- Practical applications""",
        "example": "Explain supply and demand equilibrium with a market example."
    },
    "Computer Science": {
        "icon": "💻",
        "prompt": """You are a computer science expert. Provide solutions with:
- Clear algorithmic steps
- Well-commented code examples
- Complexity analysis when relevant
- Best practices and optimization tips
- Practical implementation details""",
        "example": "Implement binary search algorithm in Python."
    }
}

def should_show_diagram(question, subject):
    """Simple diagram detection"""
    question_lower = question.lower()
    
    visual_keywords = [
        'draw', 'sketch', 'plot', 'graph', 'construct', 'visualize', 
        'diagram', 'figure', 'chart', 'show graphically', 'illustrate'
    ]
    
    for keyword in visual_keywords:
        if keyword in question_lower:
            return True
    
    # Subject-specific keywords
    if subject == "Mathematics" and any(term in question_lower for term in 
        ['parabola', 'quadratic', 'function', 'linear', 'curve', 'y=', 'sin', 'cos']):
        return True
    
    if subject == "Physics" and any(term in question_lower for term in 
        ['wave', 'trajectory', 'motion', 'circuit']):
        return True
    
    if subject == "Economics" and any(term in question_lower for term in 
        ['supply', 'demand', 'curve', 'equilibrium']):
        return True
    
    return False

def create_smart_visualization(question, subject):
    """Create simple, clean visualizations"""
    question_lower = question.lower()
    
    try:
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('white')
        
        if subject == "Mathematics":
            if any(term in question_lower for term in ['quadratic', 'parabola', 'x²', 'x^2']):
                x = np.linspace(-5, 5, 100)
                y = x**2
                ax.plot(x, y, 'b-', linewidth=2, label='y = x²')
                ax.set_title('Quadratic Function')
            elif any(term in question_lower for term in ['linear', 'y=', 'slope']):
                x = np.linspace(-5, 5, 100)
                y = 2*x + 1
                ax.plot(x, y, 'r-', linewidth=2, label='Linear Function')
                ax.set_title('Linear Function')
            elif any(term in question_lower for term in ['sin', 'cos']):
                x = np.linspace(-2*np.pi, 2*np.pi, 100)
                ax.plot(x, np.sin(x), 'b-', linewidth=2, label='sin(x)')
                ax.plot(x, np.cos(x), 'r-', linewidth=2, label='cos(x)')
                ax.set_title('Trigonometric Functions')
            
            ax.grid(True, alpha=0.3)
            ax.axhline(y=0, color='k', linewidth=0.5)
            ax.axvline(x=0, color='k', linewidth=0.5)
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.legend()
        
        elif subject == "Physics":
            t = np.linspace(0, 4*np.pi, 100)
            y = np.sin(t)
            ax.plot(t, y, 'b-', linewidth=2, label='Wave')
            ax.set_title('Wave Function')
            ax.set_xlabel('Time/Position')
            ax.set_ylabel('Amplitude')
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        elif subject == "Economics":
            x = np.linspace(0, 10, 100)
            supply = 2 * x
            demand = 20 - x
            ax.plot(x, supply, 'b-', linewidth=2, label='Supply')
            ax.plot(x, demand, 'r-', linewidth=2, label='Demand')
            ax.set_title('Supply and Demand')
            ax.set_xlabel('Quantity')
            ax.set_ylabel('Price')
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=150, facecolor='white')
        buf.seek(0)
        plt.close(fig)
        return buf
        
    except Exception:
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

def format_response(response_text):
    """Simple, clean formatting focused on readability"""
    if not response_text:
        return ""
    
    # Clean up LaTeX notation to simple text
    response_text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', response_text)
    response_text = re.sub(r'\\sqrt\{([^}]+)\}', r'sqrt(\1)', response_text)
    response_text = re.sub(r'\\[a-zA-Z]+\{?([^}]*)\}?', r'\1', response_text)
    
    lines = response_text.strip().split('\n')
    formatted_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Step headers
        if re.match(r'^\*\*Step \d+:', line):
            step_text = re.sub(r'\*\*', '', line)
            formatted_content.append(f"### {step_text}\n")
        
        # Final answer
        elif 'Final Answer' in line:
            clean_line = re.sub(r'\*\*', '', line)
            formatted_content.append(f'<div class="final-answer">{clean_line}</div>\n')
        
        # Mathematical expressions
        elif ('=' in line and any(char in line for char in ['x', '+', '-', '*', '/', '^', '(', ')'])):
            formatted_content.append(f'<div class="math-line">{line}</div>\n')
        
        # Regular text
        else:
            formatted_content.append(f"{line}\n\n")
    
    return ''.join(formatted_content)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎓 Academic Assistant Pro</h1>
        <p>Clear, step-by-step homework solutions</p>
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
        st.markdown("### 💡 Example")
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
                with st.spinner("Getting solution..."):
                    response = get_api_response(question, selected_subject)
                    
                    if response:
                        st.markdown("---")
                        st.markdown(f"## 📚 {selected_subject} Solution")
                        
                        # Simple formatting in a clean container
                        formatted_response = format_response(response)
                        st.markdown(f"""
                        <div class="solution-content">
                            {formatted_response}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show diagram if needed
                        if should_show_diagram(question, selected_subject):
                            st.markdown("### 📊 Visualization")
                            viz = create_smart_visualization(question, selected_subject)
                            if viz:
                                st.image(viz, use_container_width=True)
                        
                        # Simple feedback
                        st.markdown("### Rate this solution")
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            if st.button("👍 Helpful"):
                                st.success("Thanks!")
                        with col_b:
                            if st.button("👎 Needs work"):
                                st.info("We'll improve!")
                        with col_c:
                            if st.button("🔄 Try again"):
                                st.rerun()
            else:
                st.warning("Please enter a question.")
    
    # Simple footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🎓 Academic Assistant Pro - Focus on Learning</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
