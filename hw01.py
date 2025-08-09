# multi_subject_app.py
#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
import streamlit as st
import requests
import matplotlib.pyplot as plt
import numpy as np
import json
from io import BytesIO
import PIL.Image
import math
import re

# === FREE API Setup (Hugging Face) ===
def get_hf_headers():
    return {"Authorization": "Bearer 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"}  # Replace with your HF token

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
# Test change
headers = {
    "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
    "Content-Type": "application/json"
}

def query_subject_llm(prompt, subject="Math"):
    system_prompts = {
        "Math": "You are a math tutor. Solve step-by-step with clear explanations. Format with **Step 1**, **Step 2**, etc.",
        "English": "You are an English tutor. Help with grammar, writing, and literature analysis. Be clear and educational.",
        "Science": "You are a science tutor. Explain concepts clearly with examples and scientific reasoning.",
        "History": "You are a history tutor. Provide historical context, dates, and analyze events objectively.",
        "Geography": "You are a geography tutor. Explain locations, climate, physical features, and human geography.",
        "Physics": "You are a physics tutor. Use formulas, show calculations, and explain physical phenomena.",
        "Chemistry": "You are a chemistry tutor. Explain reactions, show equations, and describe chemical properties.",
        "Biology": "You are a biology tutor. Explain biological processes, systems, and life sciences clearly.",
        "Economics": "You are an economics tutor. Explain economic principles, theories, and real-world applications."
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
    # Basic pattern matching for triangle problems
    sides = {}
    angles = {}
    points = ["A", "B", "C"]  # Default triangle points
    
    # Extract sides (e.g., "AB = 5 cm")
    side_pattern = r'([A-Z][A-Z])\s*=\s*(\d+(?:\.\d+)?)\s*cm'
    side_matches = re.findall(side_pattern, question, re.IGNORECASE)
    for match in side_matches:
        sides[match[0].upper()] = float(match[1])
    
    # Extract angles (e.g., "∠ABC = 60°")
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

# === Simple Triangle Drawing (Math only) ===
def draw_simple_triangle(sides, points=["A", "B", "C"]):
    """Simplified triangle drawing for math problems"""
    try:
        if len(sides) >= 2:
            # Simple right triangle for demo
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
        ]
    }
    
    for i, ex in enumerate(examples.get(subject, [])[:3]):
        if st.button(f"📌 {ex}", key=f"ex_{subject}_{i}"):
            st.session_state.question_input = ex

# === Solve Button ===
if st.button("🚀 Get Solution", type="primary"):
    if question.strip():
        with st.spinner(f"🧠 Solving {subject} problem..."):
            # Get LLM solution
            solution = query_subject_llm(question, subject)
            
            st.markdown("---")
            st.subheader(f"📘 {subject} Solution:")
            st.write(solution)
            
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

st.caption("*Subject to Hugging Face free tier limits")