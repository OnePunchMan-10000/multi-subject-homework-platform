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

# Improved CSS with better spacing and fraction formatting
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
    
    /* Improved solution content styling with better spacing */
    .solution-content {
        background-color: rgba(255,255,255,0.05);
        border-left: 4px solid #4CAF50;
        padding: 2rem;
        margin: 1.5rem 0;
        border-radius: 8px;
        line-height: 1.8;
    }
    
    .solution-content h3 {
        color: #4CAF50;
        margin: 2rem 0 1rem 0;
        font-size: 1.3em;
        border-bottom: 2px solid #4CAF50;
        padding-bottom: 0.5rem;
    }
    
    .solution-content p {
        margin: 1.2rem 0;
        line-height: 1.8;
        color: #e0e0e0;
        font-size: 1.05em;
    }
    
    /* Better mathematical expression styling */
    .math-line {
        font-family: 'Courier New', monospace;
        background-color: rgba(255,193,7,0.15);
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border-radius: 6px;
        color: #ffc107;
        text-align: center;
        font-size: 1.1em;
        line-height: 1.6;
        border: 1px solid rgba(255,193,7,0.3);
    }
    
    /* Fraction display within math-line - ensure proper vertical display */
    .fraction-display {
        display: inline-block;
        text-align: center;
        margin: 0 8px;
        vertical-align: middle;
        line-height: 1.2;
    }
    
    .fraction-bar {
        border-bottom: 2px solid #ffc107;
        margin: 2px 0;
        line-height: 1;
        width: 100%;
    }
    
    /* Superscript styling for powers */
    .power {
        font-size: 0.8em;
        vertical-align: super;
        line-height: 0;
    }
    
    .final-answer {
        background-color: rgba(76,175,80,0.2);
        border: 2px solid #4CAF50;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2em;
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
2. Write mathematical expressions in plain text: use x^2 for x², sqrt(x) for square roots
3. For fractions, use format: (numerator)/(denominator) - this will be displayed properly
4. Put each mathematical equation on its own line
5. Explain the reasoning behind each step
6. End with "**Final Answer:**" 
7. Keep explanations clear and concise
8. Add blank lines between steps for better readability

FRACTION EXAMPLES:
- Write dy/dx = (2x + 1)/(x^2 + 1) 
- Write y = (x^2 + 3x + 2)/(x + 1)
- This will display with numerator over denominator in a single box

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
- Real-world context when helpful
- Add blank lines between steps for readability""",
        "example": "A 2kg object falls from 10m height. Find velocity just before impact."
    },
    "Chemistry": {
        "icon": "🧪",
        "prompt": """You are a chemistry expert. Provide solutions with:
- Clear step-by-step format
- Proper chemical equations and formulas
- Balanced equations where needed
- Clear explanations of chemical processes
- Simple, readable notation
- Add blank lines between steps for readability""",
        "example": "Balance: Al + O₂ → Al₂O₃"
    },
    "Biology": {
        "icon": "🧬",
        "prompt": """You are a biology expert. Provide clear explanations with:
- Well-organized structure
- Accurate biological terminology
- Clear examples and analogies
- Step-by-step processes where applicable
- Real-world connections
- Add blank lines between sections for readability""",
        "example": "Explain the process of cellular respiration in detail."
    },
    "English Literature": {
        "icon": "📚",
        "prompt": """You are an English literature expert. Provide analysis with:
- Clear analytical structure
- Textual evidence and examples
- Literary device explanations
- Historical/cultural context
- Well-organized arguments
- Add blank lines between points for readability""",
        "example": "Analyze the symbolism of light and darkness in Romeo and Juliet."
    },
    "History": {
        "icon": "🏛️",
        "prompt": """You are a history expert. Provide analysis with:
- Chronological or thematic organization
- Multiple perspectives and sources
- Cause-and-effect relationships
- Historical context and significance
- Clear, factual explanations
- Add blank lines between sections for readability""",
        "example": "Analyze the causes of World War I."
    },
    "Economics": {
        "icon": "💰",
        "prompt": """You are an economics expert. Provide explanations with:
- Clear economic principles
- Step-by-step calculations where needed
- Real-world examples
- Simple mathematical notation
- Practical applications
- Add blank lines between steps for readability""",
        "example": "Explain supply and demand equilibrium with a market example."
    },
    "Computer Science": {
        "icon": "💻",
        "prompt": """You are a computer science expert. Provide solutions with:
- Clear algorithmic steps
- Well-commented code examples
- Complexity analysis when relevant
- Best practices and optimization tips
- Practical implementation details
- Add blank lines between sections for readability""",
        "example": "Implement binary search algorithm in Python."
    }
}

def should_show_diagram(question: str, subject: str) -> bool:
    """Return True only when the question explicitly asks for a visual/graph/geometry construction.

    Policy:
    - Require an explicit drawing intent for algebra/calculus/trig (draw/plot/graph/sketch/construct/diagram/illustrate/visualize)
    - Always allow geometry constructions when common geometry terms appear
    - Keep other subjects conservative
    """
    q = question.lower()

    # 1) Strong drawing intent verbs
    intent = any(w in q for w in [
        'draw', 'sketch', 'plot', 'graph', 'construct', 'diagram', 'figure',
        'show graphically', 'illustrate', 'visualize'
    ])

    # 2) Geometry keywords that justify a diagram regardless of verb
    geometry_terms = [
        'triangle', ' abc', 'abc ', 'perpendicular bisector', 'angle bisector',
        'median', 'altitude', 'parallel', 'perpendicular', 'circumcircle',
        'incenter', 'circumcenter', 'square', 'rectangle', 'circle',
        'semicircle', 'polygon', 'pentagon', 'hexagon', 'heptagon', 'octagon',
        'geometry', 'tangent', 'tangents'
    ]
    if any(t in q for t in geometry_terms):
        return True

    # 3) Mathematics graphs: require intent + an equation/function pattern
    if subject == 'Mathematics':
        if intent and (
            re.search(r'\by\s*=\s*', q) or  # y = ...
            re.search(r'\bf\(x\)\s*=\s*', q) or  # f(x) = ...
            'parabola' in q or  # often implies graphing when paired with intent
            'sin' in q or 'cos' in q or 'tan' in q  # trig plots when intent present
        ):
            return True
        return False

    # 4) Physics: show only for waves/trajectories when intent present
    if subject == 'Physics':
        if intent and any(k in q for k in ['wave', 'trajectory', 'motion', 'circuit']):
            return True
        return False

    # 5) Economics: show only when intent present with supply/demand
    if subject == 'Economics':
        if intent and any(k in q for k in ['supply', 'demand', 'equilibrium', 'curve']):
            return True
        return False

    # Default: require explicit intent
    return intent

def create_smart_visualization(question: str, subject: str):
    """Create simple, clean visualizations with improved math module"""
    question_lower = question.lower()

    try:
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_facecolor('white')

        if subject == "Mathematics":
            # Simplified geometry detection - focus on most common cases
            if 'triangle' in question_lower or ' abc' in question_lower:
                # Simple triangle construction
                def extract_side_length(name: str):
                    pattern = rf"{name}\s*=?\s*(\d+(?:\.\d+)?)"
                    match = re.search(pattern, question, re.IGNORECASE)
                    return float(match.group(1)) if match else None

                # Get side lengths or use defaults
                ab = extract_side_length('AB') or 5.0
                bc = extract_side_length('BC') or 6.0
                ac = extract_side_length('AC') or 4.0

                # Create triangle with simple positioning
                B = np.array([0, 0])
                C = np.array([bc, 0])
                
                # Use law of cosines for third vertex
                cos_B = (ab**2 + bc**2 - ac**2) / (2 * ab * bc)
                cos_B = max(-1, min(1, cos_B))  # Clamp to valid range
                angle_B = np.arccos(cos_B)
                
                A = np.array([ab * np.cos(angle_B), ab * np.sin(angle_B)])

                # Draw triangle
                triangle_x = [B[0], C[0], A[0], B[0]]
                triangle_y = [B[1], C[1], A[1], B[1]]
                ax.plot(triangle_x, triangle_y, 'k-', linewidth=2)

                # Add vertices
                ax.scatter([A[0], B[0], C[0]], [A[1], B[1], C[1]], 
                          color='red', s=50, zorder=5)

                # Add labels with proper positioning
                offset = 0.3
                ax.text(A[0], A[1] + offset, 'A', fontsize=14, ha='center', fontweight='bold')
                ax.text(B[0] - offset, B[1] - offset, 'B', fontsize=14, ha='center', fontweight='bold')
                ax.text(C[0] + offset, C[1] - offset, 'C', fontsize=14, ha='center', fontweight='bold')

                # Add side lengths
                ax.text((B[0] + C[0])/2, (B[1] + C[1])/2 - 0.4, f'{bc:.0f}cm', 
                       fontsize=10, ha='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="white"))
                ax.text((A[0] + B[0])/2 - 0.4, (A[1] + B[1])/2, f'{ab:.0f}cm', 
                       fontsize=10, ha='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="white"))
                ax.text((A[0] + C[0])/2 + 0.4, (A[1] + C[1])/2, f'{ac:.0f}cm', 
                       fontsize=10, ha='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="white"))

                # Add constructions if mentioned
                if 'perpendicular bisector' in question_lower:
                    if 'bc' in question_lower:
                        mid = (B + C) / 2
                        # Perpendicular to BC
                        perp_dir = np.array([-(C[1] - B[1]), C[0] - B[0]])
                        perp_dir = perp_dir / np.linalg.norm(perp_dir) * 3
                        ax.plot([mid[0] - perp_dir[0], mid[0] + perp_dir[0]], 
                               [mid[1] - perp_dir[1], mid[1] + perp_dir[1]], 
                               'b--', linewidth=2, label='Perpendicular bisector of BC')

                if 'angle bisector' in question_lower:
                    # Simple angle bisector from A
                    bisector_end = (B + C) / 2
                    ax.plot([A[0], bisector_end[0]], [A[1], bisector_end[1]], 
                           'g--', linewidth=2, label='Angle bisector')

                ax.set_title('Triangle Construction', fontsize=16, fontweight='bold')

            elif 'circle' in question_lower:
                # Simple circle construction
                radius_match = re.search(r'radius\s*(\d+(?:\.\d+)?)', question, re.IGNORECASE)
                radius = float(radius_match.group(1)) if radius_match else 3.0

                circle = plt.Circle((0, 0), radius, fill=False, edgecolor='black', linewidth=2)
                ax.add_patch(circle)
                
                # Center point
                ax.scatter([0], [0], color='red', s=50)
                ax.text(0, -0.3, 'O', fontsize=14, ha='center', fontweight='bold')
                
                # Radius line
                ax.plot([0, radius], [0, 0], 'k--', linewidth=1)
                ax.text(radius/2, 0.2, f'{radius:.0f}cm', fontsize=10, ha='center',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="white"))

                ax.set_title('Circle', fontsize=16, fontweight='bold')

            elif 'square' in question_lower:
                # Simple square
                side = 4.0
                square_x = [0, side, side, 0, 0]
                square_y = [0, 0, side, side, 0]
                ax.plot(square_x, square_y, 'k-', linewidth=2)
                
                # Vertices
                vertices = [(0,0), (side,0), (side,side), (0,side)]
                labels = ['A', 'B', 'C', 'D']
                for (x, y), label in zip(vertices, labels):
                    ax.scatter([x], [y], color='red', s=50)
                    offset = 0.3
                    ax.text(x - offset if x > 0 else x - offset, 
                           y - offset if y > 0 else y - offset, 
                           label, fontsize=14, ha='center', fontweight='bold')

                ax.set_title('Square', fontsize=16, fontweight='bold')

            elif any(term in question_lower for term in ['parabola', 'quadratic', 'y=', 'f(x)=']):
                # Function plotting
                if 'quadratic' in question_lower or 'parabola' in question_lower:
                    x = np.linspace(-5, 5, 200)
                    y = x**2
                    ax.plot(x, y, 'b-', linewidth=3, label='y = x²')
                    ax.set_title('Quadratic Function', fontsize=16, fontweight='bold')
                elif 'linear' in question_lower:
                    x = np.linspace(-5, 5, 200)
                    y = 2*x + 1
                    ax.plot(x, y, 'r-', linewidth=3, label='y = 2x + 1')
                    ax.set_title('Linear Function', fontsize=16, fontweight='bold')
                else:
                    # Default quadratic
                    x = np.linspace(-5, 5, 200)
                    y = x**2
                    ax.plot(x, y, 'b-', linewidth=3, label='y = x²')
                    ax.set_title('Function Graph', fontsize=16, fontweight='bold')

                ax.grid(True, alpha=0.3)
                ax.axhline(y=0, color='k', linewidth=0.8)
                ax.axvline(x=0, color='k', linewidth=0.8)
                ax.set_xlabel('x', fontsize=12)
                ax.set_ylabel('y', fontsize=12)
                ax.legend(fontsize=12)

            elif any(term in question_lower for term in ['sin', 'cos', 'tan']):
                # Trigonometric functions
                x = np.linspace(-2*np.pi, 2*np.pi, 400)
                if 'sin' in question_lower:
                    ax.plot(x, np.sin(x), 'b-', linewidth=3, label='sin(x)')
                if 'cos' in question_lower:
                    ax.plot(x, np.cos(x), 'r-', linewidth=3, label='cos(x)')
                
                ax.set_title('Trigonometric Functions', fontsize=16, fontweight='bold')
                ax.grid(True, alpha=0.3)
                ax.axhline(y=0, color='k', linewidth=0.8)
                ax.axvline(x=0, color='k', linewidth=0.8)
                ax.set_xlabel('x', fontsize=12)
                ax.set_ylabel('y', fontsize=12)
                ax.legend(fontsize=12)

            else:
                # Default mathematical visualization
                x = np.linspace(-3, 3, 100)
                y = x**2
                ax.plot(x, y, 'b-', linewidth=3, label='y = x²')
                ax.grid(True, alpha=0.3)
                ax.axhline(y=0, color='k', linewidth=0.8)
                ax.axvline(x=0, color='k', linewidth=0.8)
                ax.set_xlabel('x', fontsize=12)
                ax.set_ylabel('y', fontsize=12)
                ax.legend(fontsize=12)
                ax.set_title('Mathematical Function', fontsize=16, fontweight='bold')

        elif subject == "Physics":
            # Simple wave visualization
            x = np.linspace(0, 4*np.pi, 200)
            y = np.sin(x)
            ax.plot(x, y, 'b-', linewidth=3, label='Wave Function')
            ax.set_title('Physics Wave', fontsize=16, fontweight='bold')
            ax.set_xlabel('Position/Time', fontsize=12)
            ax.set_ylabel('Amplitude', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=12)

        elif subject == "Economics":
            # Simple supply and demand
            x = np.linspace(0, 10, 100)
            supply = 2 * x + 1
            demand = 15 - x
            ax.plot(x, supply, 'b-', linewidth=3, label='Supply')
            ax.plot(x, demand, 'r-', linewidth=3, label='Demand')
            
            # Find intersection
            intersection_x = (15 - 1) / 3
            intersection_y = 2 * intersection_x + 1
            ax.scatter([intersection_x], [intersection_y], color='green', s=100, zorder=5)
            ax.text(intersection_x + 0.5, intersection_y, 'Equilibrium', fontsize=10)
            
            ax.set_title('Supply and Demand', fontsize=16, fontweight='bold')
            ax.set_xlabel('Quantity', fontsize=12)
            ax.set_ylabel('Price', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=12)

        # Set proper aspect ratio and clean up
        if subject == "Mathematics" and any(term in question_lower for term in ['triangle', 'circle', 'square']):
            ax.set_aspect('equal')
            # Auto-adjust limits with padding
            ax.relim()
            ax.autoscale()
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            x_pad = (xlim[1] - xlim[0]) * 0.1
            y_pad = (ylim[1] - ylim[0]) * 0.1
            ax.set_xlim(xlim[0] - x_pad, xlim[1] + x_pad)
            ax.set_ylim(ylim[0] - y_pad, ylim[1] + y_pad)
            ax.axis('off')  # Remove axes for geometric shapes
        
        # Add legend if present
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend(loc='best', fontsize=10)

        plt.tight_layout()
        
        # Save to buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
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

def format_powers(text):
    """Convert ^2, ^3, etc. to proper superscript format"""
    # Replace common powers with superscript
    text = re.sub(r'\^2', '<span class="power">2</span>', text)
    text = re.sub(r'\^3', '<span class="power">3</span>', text)
    text = re.sub(r'\^4', '<span class="power">4</span>', text)
    text = re.sub(r'\^(\d+)', r'<span class="power">\1</span>', text)
    text = re.sub(r'\^(\([^)]+\))', r'<span class="power">\1</span>', text)
    # Replace sqrt(...) with √(...)
    text = re.sub(r'\bsqrt\s*\(', '√(', text)
    return text

def format_fraction(numerator, denominator):
    """Format a fraction with numerator over denominator in inline style"""
    num_clean = format_powers(numerator.strip())
    den_clean = format_powers(denominator.strip())
    
    return f"""<div class="fraction-display">
        <div>{num_clean}</div>
        <div class="fraction-bar"></div>
        <div>{den_clean}</div>
    </div>"""

def format_response(response_text):
    """Improved formatting with consistent vertical fractions and tighter spacing"""
    if not response_text:
        return ""
    
    # Clean up LaTeX notation to simple text but preserve fraction structure
    response_text = re.sub(r'\\sqrt\{([^}]+)\}', r'sqrt(\1)', response_text)
    response_text = re.sub(r'\\[a-zA-Z]+\{?([^}]*)\}?', r'\1', response_text)
    
    lines = response_text.strip().split('\n')
    formatted_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            # Add minimal spacing between sections
            formatted_content.append("<br>")
            continue
        
        # Skip stray closing tags that may appear in the model text
        if re.match(r'^</(div|span|p)>$', line):
            continue

        # Step headers
        if re.match(r'^\*\*Step \d+:', line) or re.match(r'^###\s*Step \d+:', line):
            step_text = re.sub(r'\*\*|###', '', line).strip()
            formatted_content.append(f'<h3 style="color:#4CAF50;margin:1rem 0 0.5rem 0;">{step_text}</h3>')
            # extra space after each step header for readability
            formatted_content.append('<div style="height:6px"></div>')
        
        # Final answer
        elif 'Final Answer' in line:
            clean_line = re.sub(r'\*\*', '', line)
            formatted_content.append(f'<div class="final-answer">{format_powers(clean_line)}</div>\n')
        
        # Check for any line containing fractions - convert ALL to vertical display
        elif '/' in line and ('(' in line or any(char in line for char in ['x', 'y', 'dx', 'dy', 'du', 'dv'])):
            # Convert all fractions in the line to vertical display
            # First handle complex fractions like (numerator)/(denominator) - more comprehensive pattern
            formatted_line = re.sub(r'\(([^)]+)\)\s*/\s*\(([^)]+)\)', lambda m: format_fraction(m.group(1), m.group(2)), line)
            # Then handle simple fractions like du/dx, dv/dx, dy/dx
            formatted_line = re.sub(r'\b([a-zA-Z]+)/([a-zA-Z]+)\b', lambda m: format_fraction(m.group(1), m.group(2)), formatted_line)
            # Handle any remaining fractions with parentheses - catch cases like (2x + 1) / (x² + 1)²
            formatted_line = re.sub(r'\(([^)]+)\)\s*/\s*([^/\s]+)', lambda m: format_fraction(m.group(1), m.group(2)), formatted_line)
            formatted_content.append(f'<div class="math-line">{format_powers(formatted_line)}</div>\n')
        
        # Mathematical expressions with equations (no fractions)
        elif ('=' in line and any(char in line for char in ['x', '+', '-', '*', '^', '(', ')'])):
            formatted_content.append(f'<div class="math-line">{format_powers(line)}</div>\n')
        
        # Regular text
        else:
            formatted_content.append(f"{format_powers(line)}\n")
    
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
        
        subject_options =
