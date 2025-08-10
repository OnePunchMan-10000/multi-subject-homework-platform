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

# Clean, minimal CSS focused on readability
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Clean background */
    .stApp {
        background-color: #ffffff;
        color: #2c3e50;
    }
    
    /* Simple header */
    .main-header {
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        font-size: 2.5em;
        margin-bottom: 0.5rem;
        color: #2c3e50;
    }
    
    .main-header p {
        font-size: 1.2em;
        color: #7f8c8d;
        margin: 0;
    }
    
    /* Clean form elements */
    .stSelectbox > div > div {
        background-color: #f8f9fa;
        border: 2px solid #e9ecef;
        color: #2c3e50;
    }
    
    .stTextArea textarea {
        background-color: #f8f9fa !important;
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
        color: #2c3e50 !important;
        font-size: 16px !important;
        line-height: 1.5 !important;
    }
    
    .stButton > button {
        background: #3498db;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 16px;
        width: 100%;
        transition: background-color 0.3s;
    }
    
    .stButton > button:hover {
        background: #2980b9;
    }
    
    /* Textbook-style solution container */
    .solution-container {
        background: #ffffff;
        border: 2px solid #3498db;
        border-radius: 12px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Textbook-style step headers */
    .step-header {
        font-size: 1.3em;
        font-weight: bold;
        color: #2c3e50;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #ecf0f1;
    }
    
    /* Mathematical expressions */
    .math-expression {
        font-family: 'Times New Roman', serif;
        font-size: 1.2em;
        text-align: center;
        margin: 1rem 0;
        padding: 1rem;
        background: #f8f9fa;
        border-left: 4px solid #3498db;
        border-radius: 4px;
    }
    
    /* Final answer highlight */
    .final-answer {
        background: #e8f6f3;
        border: 3px solid #27ae60;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 2rem 0;
        text-align: center;
        font-size: 1.3em;
        font-weight: bold;
        color: #27ae60;
    }
    
    /* Explanation text */
    .explanation-text {
        font-size: 1.1em;
        line-height: 1.6;
        color: #2c3e50;
        margin: 1rem 0;
    }
    
    /* Subject selection styling */
    .subject-selection {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }
    
    /* Remove any box styling */
    .element-container {
        background: none !important;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced subject configurations with more detailed prompts for textbook-style answers
SUBJECTS = {
    "Mathematics": {
        "icon": "📐",
        "prompt": """You are a mathematics professor writing a detailed textbook solution. Your response should be:

1. **Structure**: Use clear step-by-step format with descriptive headers
2. **Mathematical Rigor**: Show every calculation step, no shortcuts
3. **Explanations**: Explain WHY each step is taken and what mathematical principle it uses
4. **Verification**: Always verify your final answer by substituting back or using alternative methods
5. **Formatting**: Use clear mathematical notation that's easy to read

Format your response like a textbook:
- Start with "Given:" to state what we know
- Use "Step 1: [Description]", "Step 2: [Description]", etc.
- Show all work: formula → substitution → calculation → result
- End with "Final Answer:" clearly highlighted
- Add a "Verification:" section when possible

Write in a teaching style that helps students understand the underlying concepts.""",
        "example": "Solve: 3x² - 12x + 9 = 0"
    },
    "Physics": {
        "icon": "⚡",
        "prompt": """You are a physics professor writing a comprehensive textbook solution. Your response should include:

1. **Problem Analysis**: Identify what physics concepts and principles apply
2. **Given Information**: List all known values with proper units
3. **Required**: State what we need to find
4. **Solution Strategy**: Explain the approach before starting calculations
5. **Step-by-Step Solution**: Show every calculation with units
6. **Physical Interpretation**: Explain what the answer means physically

Use proper physics methodology:
- Start with relevant equations and explain why they apply
- Show dimensional analysis
- Keep track of units throughout all calculations
- Explain the physics concepts involved
- Connect to real-world applications when relevant""",
        "example": "A 2kg object falls from 10m height. Find velocity just before impact."
    },
    "Chemistry": {
        "icon": "🧪",
        "prompt": """You are a chemistry professor providing detailed textbook-style solutions. Include:

1. **Chemical Analysis**: Identify the type of problem and relevant principles
2. **Given Information**: State all known values and chemical species
3. **Chemical Principles**: Explain the underlying chemistry concepts
4. **Balanced Equations**: Show all chemical equations properly balanced
5. **Calculations**: Show stoichiometric calculations step-by-step
6. **Units and Significant Figures**: Maintain proper scientific notation

Structure like a textbook:
- Begin with the chemical principle or law that applies
- Show molecular formulas and balanced equations
- Perform calculations with proper unit conversion
- Explain the chemical significance of the results""",
        "example": "Balance: Al + O₂ → Al₂O₃"
    },
    "Biology": {
        "icon": "🧬",
        "prompt": """You are a biology professor creating detailed educational content. Provide:

1. **Biological Context**: Explain the biological system or process involved
2. **Key Concepts**: Define important biological terms and concepts
3. **Detailed Explanation**: Break down complex processes into understandable steps
4. **Examples**: Use specific examples from living organisms
5. **Connections**: Link concepts to broader biological principles
6. **Summary**: Summarize key points for better understanding

Write in textbook style:
- Use proper biological terminology with explanations
- Include specific examples from nature
- Explain cause-and-effect relationships
- Connect molecular, cellular, and organismal levels""",
        "example": "Explain the process of cellular respiration in detail."
    },
    "English Literature": {
        "icon": "📚",
        "prompt": """You are a literature professor providing scholarly analysis. Include:

1. **Literary Context**: Provide background about the work, author, and period
2. **Textual Analysis**: Examine specific passages with close reading
3. **Literary Devices**: Identify and explain metaphors, symbolism, themes
4. **Critical Interpretation**: Offer thoughtful analysis with textual evidence
5. **Multiple Perspectives**: Consider different critical approaches
6. **Conclusion**: Synthesize findings into coherent interpretation

Structure as academic analysis:
- Use proper literary terminology
- Support all claims with textual evidence
- Consider historical and cultural context
- Write in formal, analytical tone""",
        "example": "Analyze the symbolism of light and darkness in Romeo and Juliet."
    },
    "History": {
        "icon": "🏛️",
        "prompt": """You are a history professor providing comprehensive historical analysis. Include:

1. **Historical Context**: Set the time period and background
2. **Multiple Perspectives**: Consider different viewpoints and sources
3. **Cause and Effect**: Analyze the factors that led to events
4. **Evidence**: Use specific historical facts, dates, and examples
5. **Significance**: Explain the broader historical importance
6. **Connections**: Link events to larger historical patterns

Write like a history textbook:
- Use chronological organization when appropriate
- Include specific dates, names, and places
- Consider multiple causation factors
- Maintain historical objectivity while explaining significance""",
        "example": "Analyze the causes of World War I."
    },
    "Economics": {
        "icon": "💰",
        "prompt": """You are an economics professor explaining economic concepts thoroughly. Provide:

1. **Economic Principles**: Identify relevant economic theories and concepts
2. **Graphical Analysis**: Describe graphs and models when applicable
3. **Mathematical Calculations**: Show economic calculations step-by-step
4. **Real-World Applications**: Connect theory to current economic conditions
5. **Multiple Perspectives**: Consider different economic schools of thought
6. **Policy Implications**: Discuss practical applications

Structure like economics textbook:
- Define key economic terms
- Explain underlying assumptions
- Show mathematical relationships
- Use contemporary examples
- Discuss policy relevance""",
        "example": "Explain supply and demand equilibrium with a market example."
    },
    "Computer Science": {
        "icon": "💻",
        "prompt": """You are a computer science professor providing detailed technical explanations. Include:

1. **Problem Analysis**: Break down the computational problem
2. **Algorithm Design**: Explain the approach and logic
3. **Code Implementation**: Provide clean, well-commented code
4. **Complexity Analysis**: Discuss time and space complexity
5. **Testing**: Show example inputs and outputs
6. **Alternative Approaches**: Mention other possible solutions

Structure like CS textbook:
- Explain algorithms step-by-step
- Use proper programming terminology
- Show code with clear comments
- Discuss efficiency and optimization
- Include practical applications""",
        "example": "Implement binary search algorithm in Python."
    }
}

def should_show_diagram(question, subject):
    """Enhanced diagram detection with better logic"""
    question_lower = question.lower()
    
    # Strong visual indicators
    visual_keywords = [
        'draw', 'sketch', 'plot', 'graph', 'construct', 'visualize', 
        'diagram', 'figure', 'chart', 'show graphically', 'illustrate',
        'represent visually', 'create diagram', 'make chart', 'display'
    ]
    
    for keyword in visual_keywords:
        if keyword in question_lower:
            return True
    
    # Subject-specific keywords that benefit from visualization
    subject_keywords = {
        'Mathematics': [
            'parabola', 'quadratic', 'function', 'linear', 'curve', 'slope',
            'triangle', 'circle', 'rectangle', 'angle', 'coordinate',
            'sin', 'cos', 'tan', 'trigonometric', 'x²', 'x^2', 'y=',
            'derivative', 'integral', 'limit'
        ],
        'Physics': [
            'wave', 'frequency', 'amplitude', 'projectile', 'trajectory', 
            'motion', 'force diagram', 'circuit', 'field', 'vector',
            'oscillation', 'pendulum', 'spring'
        ],
        'Chemistry': [
            'reaction rate', 'concentration', 'molecular structure', 
            'lewis structure', 'phase diagram', 'orbital', 'titration curve'
        ],
        'Biology': [
            'population growth', 'cell cycle', 'dna structure', 'ecosystem',
            'life cycle', 'growth curve', 'distribution'
        ],
        'Economics': [
            'supply', 'demand', 'curve', 'equilibrium', 'market',
            'production possibilities', 'cost curve', 'elasticity'
        ]
    }
    
    if subject in subject_keywords:
        for keyword in subject_keywords[subject]:
            if keyword in question_lower:
                return True
    
    return False

def create_smart_visualization(question, subject):
    """Create clean, educational visualizations"""
    question_lower = question.lower()
    
    try:
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Set clean, professional styling
        plt.rcParams.update({
            'font.size': 12,
            'axes.labelsize': 14,
            'axes.titlesize': 16,
            'legend.fontsize': 12,
            'xtick.labelsize': 11,
            'ytick.labelsize': 11
        })
        
        if subject == "Mathematics":
            if any(term in question_lower for term in ['x²', 'x^2', 'quadratic', 'parabola']):
                x = np.linspace(-5, 5, 400)
                y = x**2
                ax.plot(x, y, 'blue', linewidth=3, label='y = x²')
                ax.grid(True, alpha=0.3, linestyle='--')
                ax.axhline(y=0, color='black', linewidth=0.8)
                ax.axvline(x=0, color='black', linewidth=0.8)
                ax.set_xlabel('x', fontweight='bold')
                ax.set_ylabel('y', fontweight='bold')
                ax.set_title('Quadratic Function: y = x²', fontweight='bold', pad=20)
                ax.legend(loc='upper right', frameon=True, fancybox=True)
                
            elif any(term in question_lower for term in ['sin', 'cos', 'tan', 'trigonometric']):
                x = np.linspace(-2*np.pi, 2*np.pi, 400)
                y1 = np.sin(x)
                y2 = np.cos(x)
                ax.plot(x, y1, 'red', linewidth=3, label='sin(x)')
                ax.plot(x, y2, 'blue', linewidth=3, label='cos(x)')
                ax.grid(True, alpha=0.3, linestyle='--')
                ax.axhline(y=0, color='black', linewidth=0.8)
                ax.axvline(x=0, color='black', linewidth=0.8)
                ax.set_xlabel('x (radians)', fontweight='bold')
                ax.set_ylabel('y', fontweight='bold')
                ax.set_title('Trigonometric Functions', fontweight='bold', pad=20)
                ax.legend(loc='upper right', frameon=True, fancybox=True)
                ax.set_ylim(-1.5, 1.5)
                
            else:
                # Default mathematical function
                x = np.linspace(-5, 5, 100)
                y = 2*x + 1
                ax.plot(x, y, 'green', linewidth=3, label='y = 2x + 1')
                ax.grid(True, alpha=0.3, linestyle='--')
                ax.axhline(y=0, color='black', linewidth=0.8)
                ax.axvline(x=0, color='black', linewidth=0.8)
                ax.set_xlabel('x', fontweight='bold')
                ax.set_ylabel('y', fontweight='bold')
                ax.set_title('Linear Function', fontweight='bold', pad=20)
                ax.legend(loc='upper left', frameon=True, fancybox=True)
        
        elif subject == "Physics":
            if any(term in question_lower for term in ['wave', 'frequency', 'amplitude']):
                t = np.linspace(0, 4*np.pi, 400)
                y = np.sin(t)
                ax.plot(t, y, 'purple', linewidth=3, label='Wave Function')
                ax.grid(True, alpha=0.3, linestyle='--')
                ax.axhline(y=0, color='black', linewidth=0.8)
                ax.set_xlabel('Time or Position', fontweight='bold')
                ax.set_ylabel('Amplitude', fontweight='bold')
                ax.set_title('Wave Pattern', fontweight='bold', pad=20)
                ax.legend(frameon=True, fancybox=True)
                
            elif any(term in question_lower for term in ['projectile', 'trajectory', 'motion']):
                t = np.linspace(0, 2, 100)
                x = 20 * t
                y = 20 * t - 0.5 * 9.8 * t**2
                y = np.maximum(y, 0)  # Ground level
                ax.plot(x, y, 'red', linewidth=3, label='Projectile Path')
                ax.grid(True, alpha=0.3, linestyle='--')
                ax.set_xlabel('Horizontal Distance (m)', fontweight='bold')
                ax.set_ylabel('Height (m)', fontweight='bold')
                ax.set_title('Projectile Motion', fontweight='bold', pad=20)
                ax.legend(frameon=True, fancybox=True)
            
        elif subject == "Economics":
            if any(term in question_lower for term in ['supply', 'demand', 'equilibrium']):
                q = np.linspace(0, 10, 100)
                supply = 2 * q + 1
                demand = 15 - q
                
                ax.plot(q, supply, 'blue', linewidth=3, label='Supply')
                ax.plot(q, demand, 'red', linewidth=3, label='Demand')
                
                # Equilibrium point
                eq_q = 14/3
                eq_p = 2 * eq_q + 1
                ax.plot(eq_q, eq_p, 'go', markersize=10, label=f'Equilibrium ({eq_q:.1f}, {eq_p:.1f})')
                
                ax.grid(True, alpha=0.3, linestyle='--')
                ax.set_xlabel('Quantity', fontweight='bold')
                ax.set_ylabel('Price', fontweight='bold')
                ax.set_title('Supply and Demand Analysis', fontweight='bold', pad=20)
                ax.legend(frameon=True, fancybox=True)
        
        # Clean up the plot
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(0.8)
        ax.spines['bottom'].set_linewidth(0.8)
        
        # Save plot
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=150, 
                   facecolor='white', edgecolor='none')
        buf.seek(0)
        plt.close(fig)
        
        return buf
        
    except Exception as e:
        plt.close('all')
        return None

def get_api_response(question, subject):
    """Get enhanced response from API"""
    if 'OPENROUTER_API_KEY' not in st.secrets:
        st.error("⚠️ API key not configured. Please add OPENROUTER_API_KEY to Streamlit secrets.")
        return None
    
    api_key = st.secrets['OPENROUTER_API_KEY']
    
    system_prompt = SUBJECTS[subject]['prompt']
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "openai/gpt-4o-mini",  # Using better model for more detailed responses
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question}
        ],
        "temperature": 0.1,
        "max_tokens": 2000  # Increased for more detailed responses
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
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def format_textbook_response(response_text, subject):
    """Format response in clean textbook style"""
    
    # Clean up the response
    formatted = response_text.strip()
    
    # Split into sections
    sections = []
    current_section = ""
    
    lines = formatted.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Detect section headers
        if (line.startswith('**') and line.endswith('**')) or \
           (line.startswith('Step ') and ':' in line) or \
           line.startswith('Given:') or line.startswith('Solution:') or \
           line.startswith('Final Answer:') or line.startswith('Verification:'):
            
            if current_section:
                sections.append(current_section)
            current_section = line
        else:
            current_section += "\n" + line
    
    if current_section:
        sections.append(current_section)
    
    # Format each section
    html_output = []
    
    for section in sections:
        lines = section.split('\n')
        header = lines[0].strip()
        content = '\n'.join(lines[1:]).strip()
        
        # Clean header
        clean_header = header.replace('**', '').strip()
        
        # Format based on header type
        if 'Final Answer' in clean_header or 'Answer:' in clean_header:
            html_output.append(f'''
            <div class="final-answer">
                <strong>{clean_header}</strong><br>
                {content}
            </div>
            ''')
        
        elif clean_header.startswith('Step ') or 'Given:' in clean_header or 'Solution:' in clean_header:
            html_output.append(f'''
            <div class="step-header">{clean_header}</div>
            <div class="explanation-text">{content}</div>
            ''')
        
        elif any(symbol in content for symbol in ['=', '+', '-', '×', '÷', '^', '²', '³']) and len(content) < 200:
            # Mathematical expressions
            html_output.append(f'''
            <div class="step-header">{clean_header}</div>
            <div class="math-expression">{content}</div>
            ''')
        
        else:
            # Regular explanation
            html_output.append(f'''
            <div class="step-header">{clean_header}</div>
            <div class="explanation-text">{content}</div>
            ''')
    
    return ''.join(html_output)

def main():
    # Simple, clean header
    st.markdown("""
    <div class="main-header">
        <h1>🎓 Academic Assistant</h1>
        <p>Textbook-quality explanations for all subjects</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 📖 Select Subject")
        
        subject_options = [f"{info['icon']} {subject}" for subject, info in SUBJECTS.items()]
        selected_display = st.selectbox(
            "Choose subject:",
            subject_options,
            help="Select your academic subject"
        )
        
        selected_subject = selected_display.split(' ', 1)[1]
        
        # Simple example
        with st.expander("💡 See example"):
            st.write(f"**{selected_subject}**")
            st.write(SUBJECTS[selected_subject]['example'])
    
    with col2:
        st.markdown("### ❓ Your Question")
        
        question = st.text_area(
            "Enter your question:",
            height=150,
            placeholder=f"Ask your {selected_subject} question here...",
        )
        
        if st.button("🎯 Get Detailed Solution", type="primary"):
            if question.strip():
                with st.spinner("Creating detailed solution..."):
                    response = get_api_response(question, selected_subject)
                    
                    if response:
                        # Display solution in textbook style
                        st.markdown("---")
                        
                        formatted_response = format_textbook_response(response, selected_subject)
                        
                        st.markdown(f"""
                        <div class="solution-container">
                            <h2 style="color: #2c3e50; margin-bottom: 1.5rem; text-align: center;">
                                {SUBJECTS[selected_subject]['icon']} {selected_subject} Solution
                            </h2>
                            {formatted_response}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add diagram if appropriate
                        if should_show_diagram(question, selected_subject):
                            with st.spinner("Creating visualization..."):
                                viz = create_smart_visualization(question, selected_subject)
                                if viz:
                                    st.markdown("### 📊 Visual Representation")
                                    st.image(viz, use_column_width=True)
                        
                        # Simple feedback
                        st.markdown("---")
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            if st.button("👍 Helpful"):
                                st.success("Thank you!")
                        with col_b:
                            if st.button("👎 Needs work"):
                                st.info("We'll improve!")
                        with col_c:
                            if st.button("🔄 New solution"):
                                st.rerun()
            else:
                st.warning("Please enter a question.")

if __name__ == "__main__":
    main()
