import streamlit as st
import requests
import matplotlib.pyplot as plt
import numpy as np
import json
from io import BytesIO
import PIL.Image
import math
import re

# Hide Streamlit UI elements
hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {visibility: hidden;}
.stDecoration {visibility: hidden;}
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Clean, minimal dark theme CSS
st.markdown("""
<style>
    .stApp {
        background-color: #1a1a1a;
        color: #e0e0e0;
    }
    
    .main-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 40px 20px;
    }
    
    .problem-section {
        margin-bottom: 40px;
        background-color: #1a1a1a;
        border: none;
        padding: 0;
    }
    
    .section-title {
        color: #ffffff;
        font-size: 18px;
        font-weight: 500;
        margin-bottom: 15px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-family: 'Segoe UI', sans-serif;
    }
    
    .problem-text {
        color: #cccccc;
        font-size: 16px;
        margin-bottom: 20px;
        line-height: 1.8;
        font-family: 'Segoe UI', sans-serif;
    }
    
    .step-title {
        color: #ffffff;
        font-size: 16px;
        font-weight: 600;
        margin: 30px 0 15px 0;
        font-family: 'Segoe UI', sans-serif;
    }
    
    .step-content {
        color: #cccccc;
        font-size: 15px;
        margin-bottom: 15px;
        line-height: 1.7;
        font-family: 'Segoe UI', sans-serif;
    }
    
    .equation-display {
        background-color: #2a2a2a;
        border: 1px solid #404040;
        border-radius: 6px;
        padding: 15px 20px;
        font-family: 'Courier New', monospace;
        font-size: 18px;
        color: #ffffff;
        margin: 15px 0;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    
    .final-answer-section {
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #404040;
    }
    
    .final-answer {
        color: #ffffff;
        font-size: 16px;
        font-weight: 500;
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Hide Streamlit elements */
    .stSelectbox > div > div {
        background-color: #2a2a2a;
        color: #ffffff;
        border: 1px solid #404040;
    }
    
    .stTextArea > div > div > textarea {
        background-color: #2a2a2a;
        color: #ffffff;
        border: 1px solid #404040;
        font-family: 'Segoe UI', sans-serif;
        font-size: 16px;
        line-height: 1.5;
        resize: vertical;
        min-height: 120px;
    }
    
    .stButton > button {
        background-color: #4a4a4a;
        color: #ffffff;
        border: 1px solid #404040;
        font-family: 'Segoe UI', sans-serif;
    }
    
    .stButton > button:hover {
        background-color: #5a5a5a;
        border: 1px solid #606060;
    }
    
    /* Remove padding and margins */
    .css-1d391kg, .css-12oz5g7 {
        padding: 0;
    }
    
    .block-container {
        padding: 20px;
        max-width: 900px;
    }
    
</style>
""", unsafe_allow_html=True)

# API Setup
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

def format_clean_solution(response_text, subject):
    """Format solution in clean, minimal style with proper mathematical notation"""
    
    html_output = '<div class="problem-section">'
    
    # Split response into lines for processing
    lines = response_text.split('\n')
    current_explanation = ""
    step_counter = 1
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_explanation:
                html_output += f'<div class="step-content">{current_explanation}</div>'
                current_explanation = ""
            continue
            
        # Check if line contains step information
        if re.search(r'step\s*\d*:?', line, re.IGNORECASE):
            if current_explanation:
                html_output += f'<div class="step-content">{current_explanation}</div>'
                current_explanation = ""
            
            step_match = re.search(r'step\s*(\d*):?\s*(.*)', line, re.IGNORECASE)
            if step_match:
                step_num = step_match.group(1) if step_match.group(1) else str(step_counter)
                step_content = step_match.group(2) if step_match.group(2) else "Continue with calculation"
                html_output += f'<div class="step-title">Step {step_num}</div>'
                if step_content:
                    # Clean up mathematical notation
                    step_content = fix_math_notation(step_content)
                    html_output += f'<div class="step-content">{step_content}</div>'
                step_counter += 1
            continue
        
        # Check if line contains mathematical expressions or formulas
        if re.search(r'[=+\-*/^()²³√∫∂]', line) and len(line) < 200:
            # Clean up mathematical notation for display
            clean_line = fix_math_notation(line)
            html_output += f'<div class="equation-display">{clean_line}</div>'
        # Check for final answers or conclusions
        elif any(word in line.lower() for word in ['therefore', 'thus', 'answer', 'solution is', 'result', 'final']):
            clean_line = fix_math_notation(line)
            html_output += f'<div class="final-answer-section"><div class="section-title">Final Answer</div><div class="final-answer">{clean_line}</div></div>'
        else:
            clean_line = fix_math_notation(line)
            current_explanation += clean_line + " "
    
    # Add any remaining explanation
    if current_explanation:
        html_output += f'<div class="step-content">{current_explanation}</div>'
    
    html_output += '</div>'
    return html_output

def fix_math_notation(text):
    """Fix mathematical notation for proper display"""
    # Replace common mathematical symbols
    replacements = {
        'x^2': 'x²',
        'x^3': 'x³',
        'x^4': 'x⁴',
        'x^5': 'x⁵',
        '^2': '²',
        '^3': '³',
        '^4': '⁴',
        '^5': '⁵',
        'sqrt(': '√(',
        'derivative': 'derivative',
        'integral': '∫',
        'partial': '∂',
        '+-': '±',
        '+/-': '±',
        'pi': 'π',
        'theta': 'θ',
        'alpha': 'α',
        'beta': 'β',
        'gamma': 'γ',
        'delta': 'δ',
        'infinity': '∞',
        'sum': '∑',
        'product': '∏',
        '<=': '≤',
        '>=': '≥',
        '!=': '≠',
        'approximately': '≈',
        'approx': '≈'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text

# Minimal interface
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Input section at top (minimal)
col1, col2 = st.columns([1, 5])
with col1:
    subject = st.selectbox("", options=["Math", "English", "Science", "History", "Geography", "Physics", "Chemistry", "Biology", "Economics"], label_visibility="collapsed")

with col2:
    question = st.text_area("", placeholder="Enter your homework question here...", height=120, label_visibility="collapsed")

if st.button("Solve", type="primary"):
    if question.strip():
        # Show example solution immediately for demo
        if "quadratic" in question.lower() or "2x" in question or "derivative" in question.lower():
            if "derivative" in question.lower():
                example_solution = """Step 1: Identify the function and apply differentiation rules.

Given: y = x² + (1/x) - 1

We need to find dy/dx by differentiating each term separately.

Step 2: Differentiate the term x².

The derivative of x² with respect to x is 2x.

Step 3: Differentiate the term (1/x).

Rewrite 1/x as x⁻¹
The derivative of x⁻¹ with respect to x is -1·x⁻² = -1/x²

Step 4: Differentiate the constant term -1.

The derivative of any constant is 0.

Step 5: Combine all derivatives.

dy/dx = 2x + (-1/x²) + 0
dy/dx = 2x - 1/x²

Final Answer: The derivative is dy/dx = 2x - 1/x²"""
            else:
                example_solution = """Step 1: Identify the coefficients in the quadratic equation ax² + bx + c = 0.

Given equation: 2x² + 5x - 3 = 0

a = 2, b = 5, c = -3

Step 2: Apply the quadratic formula.

x = (-b ± √(b² - 4ac)) / 2a

Step 3: Substitute the values and simplify.

x = (-5 ± √(5² - 4(2)(-3))) / 2(2)
x = (-5 ± √(25 + 24)) / 4
x = (-5 ± √49) / 4
x = (-5 ± 7) / 4

Therefore, x = (-5 + 7)/4 = 1/2 or x = (-5 - 7)/4 = -3

Final Answer: The solutions are x = 1/2 and x = -3."""
        else:
            # Get actual solution from API
            with st.spinner("Solving..."):
                example_solution = query_subject_llm(question, subject)
        
        # Display solution
        formatted_solution = format_clean_solution(example_solution, subject)
        st.markdown(formatted_solution, unsafe_allow_html=True)
    else:
        st.warning("Please enter a question first!")

st.markdown('</div>', unsafe_allow_html=True)
