# --------------- Academic Assistant Pro (circle-only visualiser) ---------------
import streamlit as st
import requests
import json
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import re

# Page config
st.set_page_config(
    page_title="Academic Assistant Pro",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp {background-color:#0e1117;color:white;}
    .main-header {text-align:center;padding:1.5rem 0;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;border-radius:10px;margin-bottom:2rem;}
    .solution-content{background-color:rgba(255,255,255,0.05);border-left:4px solid #4CAF50;padding:2rem;margin:1.5rem 0;border-radius:8px;line-height:1.8;}
    .math-line{font-family:'Courier New',monospace;background-color:rgba(255,193,7,0.15);padding:1rem 1.5rem;margin:1rem 0;border-radius:6px;color:#ffc107;text-align:center;font-size:1.1em;border:1px solid rgba(255,193,7,0.3);}
    .final-answer{background-color:rgba(76,175,80,0.2);border:2px solid #4CAF50;padding:1.5rem;margin:1.5rem 0;border-radius:8px;text-align:center;font-weight:bold;font-size:1.2em;}
    .stTextArea textarea{background-color:rgba(255,255,255,0.1)!important;border:2px solid rgba(255,255,255,0.3)!important;border-radius:8px!important;color:white!important;}
    .stButton>button{background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;border:none;border-radius:8px;padding:.5rem 2rem;font-weight:600;width:100%;}
</style>
""", unsafe_allow_html=True)

SUBJECTS = {
    "Mathematics": {"icon":"📐","prompt":"You are an expert maths tutor. Provide step-by-step solutions.","example":"Solve: 3x² - 12x + 9 = 0"},
    "Physics": {"icon":"⚡","prompt":"You are a physics expert. Provide clear step-by-step solutions.","example":"A 2 kg object falls from 10 m. Find impact velocity."},
    "Chemistry": {"icon":"🧪","prompt":"You are a chemistry expert. Provide clear step-by-step solutions.","example":"Balance: Al + O₂ → Al₂O₃"},
    "Biology": {"icon":"🧬","prompt":"You are a biology expert. Provide clear explanations.","example":"Explain cellular respiration."},
    "English Literature": {"icon":"📚","prompt":"You are an English expert. Provide clear analysis.","example":"Symbolism in Romeo & Juliet."},
    "History": {"icon":"🏛️","prompt":"You are a history expert. Provide clear analysis.","example":"Causes of World War I."},
    "Economics": {"icon":"💰","prompt":"You are an economics expert. Provide clear explanations.","example":"Explain supply and demand."},
    "Computer Science": {"icon":"💻","prompt":"You are a CS expert. Provide clear code and explanations.","example":"Binary search in Python."}
}

# ---------- Circle-only visualiser ----------
def create_smart_visualization(question: str, subject: str):
    if subject != "Mathematics":
        return None
    m = re.search(r'circle.*?(\d+(?:\.\d+)?)\s*cm', question.lower())
    if not m:
        return None
    r = float(m.group(1))
    fig, ax = plt.subplots(figsize=(6, 6))
    fig.patch.set_facecolor('white')
    circle = plt.Circle((0, 0), r, fill=False, color='black', linewidth=2)
    ax.add_patch(circle)
    ax.scatter([0], [0], color='black')
    ax.text(0, 0.2, 'O', ha='center', va='bottom', color='black')
    ax.plot([0, r], [0, 0], '--', color='black')
    ax.text(r/2, 0.15, f'{r} cm', ha='center', va='bottom', color='black')
    ax.set_aspect('equal')
    ax.set_xlim(-r-1, r+1)
    ax.set_ylim(-r-1, r+1)
    ax.axis('off')
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, facecolor='white')
    buf.seek(0)
    plt.close(fig)
    return buf
# -------------------------------------------

def should_show_diagram(question: str, subject: str) -> bool:
    return bool(re.search(r'circle.*?(\d+(?:\.\d+)?)\s*cm', question.lower()))

def get_api_response(question, subject):
    if 'OPENROUTER_API_KEY' not in st.secrets:
        st.error("⚠️ API key not configured. Add OPENROUTER_API_KEY to secrets.")
        return None
    api_key = st.secrets['OPENROUTER_API_KEY']
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {"model":"openai/gpt-4o-mini","messages":[{"role":"system","content":SUBJECTS[subject]['prompt']},{"role":"user","content":question}],"temperature":0.1,"max_tokens":2000}
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        st.error(f"API Error: {response.status_code}")
    except Exception as e:
        st.error(f"Network Error: {e}")
    return None

def format_powers(text):
    text = re.sub(r'\^(\d+)', r'<span class="power">\1</span>', text)
    text = re.sub(r'\bsqrt\s*\(', '√(', text)
    return text

def format_response(response_text):
    lines = response_text.strip().split('\n')
    out = []
    for line in lines:
        line = line.strip()
        if not line:
            out.append('<br>')
            continue
        if re.match(r'^\*\*Step \d+:', line):
            out.append(f'<h3 style="color:#4CAF50;margin:1rem 0 0.5rem 0;">{line}</h3>')
        elif 'Final Answer' in line:
            out.append(f'<div class="final-answer">{format_powers(line)}</div>')
        elif '/' in line and ('x' in line or 'y' in line):
            out.append(f'<div class="math-line">{format_powers(line)}</div>')
        elif '=' in line:
            out.append(f'<div class="math-line">{format_powers(line)}</div>')
        else:
            out.append(f'{format_powers(line)}')
    return ''.join(out)

def main():
    st.markdown('<div class="main-header"><h1>🎓 Academic Assistant Pro</h1><p>Clear, step-by-step homework solutions</p></div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### 📖 Select Subject")
        selected_display = st.selectbox("Choose:", [f"{info['icon']} {sub}" for sub, info in SUBJECTS.items()])
        selected = selected_display.split(' ', 1)[1]
        st.info(f"**{selected}**: {SUBJECTS[selected]['example']}")
    with col2:
        st.markdown("### ❓ Your Question")
        question = st.text_area("Enter question:", height=120, placeholder=f"Ask your {selected} question...")
        if st.button("🎯 Get Solution", type="primary") and question.strip():
            with st.spinner("Getting solution..."):
                resp = get_api_response(question, selected)
                if resp:
                    st.markdown("---")
                    st.markdown(f"## 📚 {selected} Solution")
                    st.markdown(f'<div class="solution-content">{format_response(resp)}</div>', unsafe_allow_html=True)
                    if should_show_diagram(question, selected):
                        st.markdown("### 📊 Visualization")
                        img = create_smart_visualization(question, selected)
                        if img:
                            st.image(img, use_container_width=True)
    st.markdown('<div style="text-align:center;color:#666;padding:1rem"><p>🎓 Academic Assistant Pro - Focus on Learning</p></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
