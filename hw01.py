import streamlit as st
import requests
import matplotlib.pyplot as plt
import numpy as np
import json
from io import BytesIO
import PIL.Image
import math
import re

# === ENHANCED STYLING CSS ===
st.markdown("""
<style>
    .step-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 20px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 16px;
        margin: 15px 0 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .equation-box {
        background-color: #f8f9fa;
        border: 2px solid #e9ecef;
        border-radius: 8px;
        padding: 15px;
        font-family: 'Courier New', monospace;
        font-size: 18px;
        text-align: center;
        margin: 10px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .explanation-text {
        background-color: #f8f9fa;
        padding: 12px 16px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
        border-radius: 0 8px 8px 0;
        font-size: 14px;
        line-height: 1.6;
    }
    
    .solution-container {
        border: 1px solid #dee2e6;
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
        background: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.07);
    }
    
    .subject-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    
    .math-badge { background: #e3f2fd; color: #1565c0; }
    .english-badge { background: #f3e5f5; color: #7b1fa2; }
    .science-badge { background: #e8f5e8; color: #2e7d32; }
    .history-badge { background: #fff3e0; color: #ef6c00; }
    .geography-badge { background: #e0f2f1; color: #00695c; }
    .physics-badge { background: #fce4ec; color: #c2185b; }
    .chemistry-badge { background: #f1f8e9; color: #558b2f; }
    .biology-badge { background: #fff8e1; color: #f57f17; }
    .economics-badge { background: #e8eaf6; color: #3f51b5; }
    
    .final-answer {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        font-weight: bold;
        text-align: center;
        margin: 15px 0;
        box-shadow: 0 3px 6px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# === ENHANCED OUTPUT FORMATTING FUNCTIONS ===
def get_subject_badge(subject):
    """Return HTML for subject badge"""
    badge_class = subject.lower() + "-badge"
    return f'<span class="subject-badge {badge_class}">{subject}</span>'

def format_solution_output(response_text, subject):
    """Enhanced formatting for solution output with proper separation"""
    
    # Start the solution container
    html_output = '<div class="solution-container">'
    html_output += get_subject_badge(subject)
    html_output += f'<h3>📚 {subject} Solution:</h3>'
    
    # If response is too short or doesn't have steps, show raw content
    if len(response_text.strip()) < 50 or not re.search(r'step', response_text, re.IGNORECASE):
        html_output += f'<div class="explanation-text">{response_text}</div>'
        html_output += '</div>'
        return html_output
    
    # Split response into lines for processing
    lines = response_text.split('\n')
    current_explanation = ""
    step_counter = 1
    found_steps = False
    
    for line in lines:
        line = line.strip()
        if not line:
            # Add accumulated explanation before empty line
            if current_explanation:
                html_output += f'<div class="explanation-text">{current_explanation}</div>'
                current_explanation = ""
            continue
            
        # Check if line contains step information
        if re.search(r'step\s*\d*:?', line, re.IGNORECASE):
            found_steps = True
            # Add previous explanation if exists
            if current_explanation:
                html_output += f'<div class="explanation-text">{current_explanation}</div>'
                current_explanation = ""
            
            # Extract step information
            step_match = re.search(r'step\s*(\d*):?\s*(.*)', line, re.IGNORECASE)
            if step_match:
                step_num = step_match.group(1) if step_match.group(1) else str(step_counter)
                step_content = step_match.group(2) if step_match.group(2) else "Continue with calculation"
                html_output += f'<div class="step-header">📝 Step {step_num}: {step_content}</div>'
                step_counter += 1
            continue
        
        # Check if line contains mathematical expressions or formulas
        if re.search(r'[=+\-*/^()]', line) and len(line) < 150:
            # This looks like an equation or formula
            html_output += f'<div class="equation-box">{line}</div>'
        # Check for final answers or conclusions
        elif any(word in line.lower() for word in ['therefore', 'thus', 'answer', 'solution is', 'result', 'final']):
            html_output += f'<div class="final-answer">🎯 {line}</div>'
        else:
            # Regular explanation text - always include it
            current_explanation += line + " "
    
    # Add any remaining explanation
    if current_explanation:
        html_output += f'<div class="explanation-text">{current_explanation}</div>'
    
    # If no steps were found, show the entire response as explanation
    if not found_steps and not current_explanation:
        html_output += f'<div class="explanation-text">{response_text}</div>'
    
    html_output += '</div>'
    return html_output

# === FREE API Setup (Hugging Face) ===
def get_hf_headers():
    return {"Authorization": f"Bearer {st.secrets.get('HUGGINGFACE_TOKEN', 'your-token-here')}"}

# Subject-specific model endpoints
SUBJECT_MODELS = {
    "Math": "microsoft/DialoGPT-medium",
    "English": "facebook/blenderbot-400M-distill", 
    "Science": "allenai/unifiedqa-t5-base",
    "History": "microsoft/DialoGPT-medium",
    "Geography": "microsoft/DialoGPT-medium",
    "Physics": "allenai/unifiedqa-t5-base",
    "Chemistry": "allenai/unifiedqa-t5-base",
    "Biology": "allenai/unifiedqa-t5-base",
    "Economics": "microsoft/DialoGPT-medium"
}

# === OpenRouter API Setup (YOUR WORKING SETUP) ===
API_URL = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
    "Content-Type": "application/json"
}

def query_subject_llm(prompt, subject="Math"):
    system_prompts = {
        "Math": "You are a math tutor. Solve step-by-step with clear explanations. Format as 'Step 1: [Brief action]' then explain in detail on next lines. Put equations on separate lines.",
        "English": "You are an English tutor. Help with grammar, writing, and literature analysis. Use 'Step 1: [Brief action]' format then detailed explanation on following lines.",
        "Science": "You are a science tutor. Explain concepts clearly with examples. Use 'Step 1: [Brief action]' then detailed explanation and formulas on separate lines.",
        "History": "You are a history tutor. Provide historical context and analysis. Use 'Step 1: [Brief topic]' then detailed analysis on following lines.",
        "Geography": "You are a geography tutor. Explain locations, climate, and physical features. Use 'Step 1: [Brief topic]' then detailed explanation.",
        "Physics": "You are a physics tutor. Use formulas and show calculations step-by-step. Format as 'Step 1: [Brief action]' then explanation, then formulas on separate lines.",
        "Chemistry": "You are a chemistry tutor. Explain reactions and show equations step-by-step. Use 'Step 1: [Brief action]' then explanation, then equations on separate lines.",
        "Biology": "You are a biology tutor. Explain biological processes clearly. Use 'Step 1: [Brief process]' then detailed explanation on following lines.",
        "Economics": "You are an economics tutor. Explain economic principles and theories. Use 'Step 1: [Brief concept]' then detailed analysis on following lines."
    }
    
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "temperature": 0.3,
        "messages": [
            {"role": "system", "content": system_prompts.get(subject, "You are a helpful educational tutor.")},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
        else:
            return f"Error: {resp.status_code} - {resp.text}"
    except Exception as e:
        return f"Error: {str(e)}"

# === Geometry Functions (Keep for Math subject) ===
def extract_triangle_json(question):
    """Simplified triangle extraction for math geometry problems"""
    sides = {}
    angles = {}
    points = ["A", "B", "C"]
    
    # Extract sides
    side_pattern = r'([A-Z][A-Z])\s*=\s*(\d+(?:\.\d+)?)\s*cm'
    side_matches = re.findall(side_pattern, question, re.IGNORECASE)
    for match in side_matches:
        sides[match[0].upper()] = float(match[1])
    
    # Extract angles
    angle_pattern = r'∠([A-Z]+)\s*=\s*(\d+(?:\.\d+)?)\s*°?'
    angle_matches = re.findall(angle_pattern, question, re.IGNORECASE)
    for match in angle_matches:
        angles[match[0].upper()] = float(match[1])
    
    if sides or angles:
        return {
            "points": points,
            "sides": sides,
            "angles": angles,
            "triangle_type": "SSS" if len(sides) == 3 else "SAS" if len(sides) == 2 and len(angles) == 1 else "ASA"
        }
    return None

def draw_simple_triangle(sides, points=["A", "B", "C"]):
    """Simplified triangle drawing for math problems"""
    try:
        if len(sides) >= 2:
            fig, ax = plt.subplots(figsize=(6, 6))
            
            # Create a simple triangle
            P1 = (0, 0)
            P2 = (list(sides.values())[0], 0)
            P3 = (0, list(sides.values())[1] if len(sides) > 1 else 3)
            
            coords = np.array([P1, P2, P3, P1])
            ax.plot(coords[:, 0], coords[:, 1], 'b-', linewidth=2)
            
            # Label points
            ax.text(P1[0]-0.2, P1[1]-0.2, points[0], fontsize=12)
            ax.text(P2[0]+0.1, P2[1]-0.2, points[1], fontsize=12)
            ax.text(P3[0]-0.2, P3[1]+0.1, points[2], fontsize=12)
            
            ax.set_aspect('equal')
            ax.grid(True, alpha=0.3)
            ax.set_title("Triangle Diagram")
            
            return fig
    except Exception as e:
        print(f"Drawing error: {e}")
    return None

# === Streamlit UI ===
st.set_page_config(layout="wide", page_title="Multi-Subject LLM Homework Platform")

st.title("🎓 Multi-Subject Homework Helper")
st.markdown("*Powered by 9 specialized LLM models - completely FREE!*")

# === Subject Selection ===
col1, col2 = st.columns([2, 3])

with col1:
    subject = st.selectbox(
        "📚 Choose Subject:",
        options=list(SUBJECT_MODELS.keys()),
        index=0
    )
    
    # Show model info
    model_name = SUBJECT_MODELS[subject]
    st.info(f"Using: `{model_name}`")

with col2:
    st.markdown(f"### {subject} Homework Helper")
    
    # Subject-specific placeholders
    placeholders = {
        "Math": "Enter your math problem (e.g., 'Solve: 2x + 5 = 15' or 'Draw triangle ABC with AB=5cm, BC=6cm, ∠ABC=60°')",
        "English": "Ask about grammar, writing, or literature (e.g., 'Explain the theme of Romeo and Juliet')",
        "Science": "Ask science questions (e.g., 'What is photosynthesis?' or 'Explain Newton's laws')",
        "History": "Ask about historical events (e.g., 'Causes of World War I')",
        "Geography": "Ask about places, climate, etc. (e.g., 'Climate of Amazon rainforest')",
        "Physics": "Physics problems (e.g., 'Calculate force when mass=10kg, acceleration=5m/s²')",
        "Chemistry": "Chemistry questions (e.g., 'Balance: H2 + O2 → H2O')",
        "Biology": "Biology topics (e.g., 'Explain cell division')",
        "Economics": "Economic concepts (e.g., 'What is supply and demand?')"
    }

# === Question Input ===
question = st.text_area(
    "Enter your question:",
    placeholder=placeholders.get(subject, "Enter your homework question here..."),
    height=120
)

# === Quick Examples per Subject ===
with st.expander(f"📝 {subject} Example Questions"):
    examples = {
        "Math": [
            "Solve: 3x - 7 = 14",
            "Find area of circle with radius 5cm",
            "Draw triangle ABC with AB=4cm, BC=5cm, AC=6cm"
        ],
        "English": [
            "Correct this sentence: 'Me and him went to store'",
            "Explain the symbolism in 'The Great Gatsby'",
            "Write a thesis statement about climate change"
        ],
        "Science": [
            "What happens during photosynthesis?",
            "Explain the water cycle",
            "What are the states of matter?"
        ],
        "History": [
            "What caused the American Civil War?",
            "Explain the Industrial Revolution",
            "Who were the key figures in World War II?"
        ],
        "Geography": [
            "What is the climate of the Sahara Desert?",
            "Explain plate tectonics",
            "Where are the Rocky Mountains located?"
        ],
        "Physics": [
            "Calculate force when mass=10kg, acceleration=5m/s²",
            "Explain Newton's three laws of motion",
            "What is electromagnetic induction?"
        ],
        "Chemistry": [
            "Balance: H2 + O2 → H2O",
            "Explain the difference between ionic and covalent bonds",
            "What happens during photosynthesis chemically?"
        ],
        "Biology": [
            "Explain cell division process",
            "How does DNA replication work?",
            "What is the difference between mitosis and meiosis?"
        ],
        "Economics": [
            "What is supply and demand?",
            "Explain inflation and its causes",
            "What is GDP and how is it calculated?"
        ]
    }
    
    for i, ex in enumerate(examples.get(subject, [])[:3]):
        if st.button(f"📌 {ex}", key=f"ex_{subject}_{i}"):
            question = ex

# === Solve Button ===
if st.button("🚀 Get Solution", type="primary"):
    if question.strip():
        with st.spinner(f"🧠 Solving {subject} problem..."):
            # Get LLM solution
            solution = query_subject_llm(question, subject)
            
            st.markdown("---")
            
            # ENHANCED: Use formatted output instead of plain text
            formatted_solution = format_solution_output(solution, subject)
            st.markdown(formatted_solution, unsafe_allow_html=True)
            
            # Special handling for Math geometry
            if subject == "Math" and any(word in question.lower() for word in ["triangle", "draw", "construct"]):
                triangle_data = extract_triangle_json(question)
                if triangle_data and triangle_data["sides"]:
                    st.markdown("### 📐 Diagram:")
                    fig = draw_simple_triangle(triangle_data["sides"], triangle_data["points"])
                    if fig:
                        st.pyplot(fig)
                    else:
                        st.info("Could not generate diagram automatically")
            
            # Add expandable raw solution text
            with st.expander("📋 Raw Solution Text (for copying)"):
                st.text_area("Copy this text:", solution, height=200)
                
    else:
        st.warning("⚠️ Please enter a question first!")

# === Footer ===
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Subjects Available", "9")
with col2:
    st.metric("Cost", "$0.00")
with col3:
    st.metric("API Calls", "Unlimited*")

st.caption("*Subject to OpenRouter free tier limits")
