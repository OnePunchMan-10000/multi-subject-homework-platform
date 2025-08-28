"""EduLLM - Complete AI Study Assistant with Professional UI"""
# Updated: 2025-08-26 - Fixed UI spacing and centering issues

import streamlit as st
import requests
import json
import os
import hashlib
import matplotlib.pyplot as plt
import numpy as np
import io

# Set page config with crown branding
st.set_page_config(
    page_title="👑 EduLLM - AI Study Assistant",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'landing'
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'selected_subject' not in st.session_state:
    st.session_state.selected_subject = None
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'auth_tab' not in st.session_state:
    st.session_state.auth_tab = 'login'
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Professional CSS Styling
def load_css():
    # Gold/Silver/Black gradient theme for all pages
    bg_color = "linear-gradient(135deg, #FFD700 0%, #C0C0C0 25%, #2C2C2C 50%, #000000 75%, #FFD700 100%)"
    text_color = "#FFFFFF"
    card_bg = "rgba(255, 255, 255, 0.15)"
    subtitle_color = "#F0F0F0"

    st.markdown(f"""
    <style>
    /* Hide Streamlit default elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    .stDeployButton {{visibility: hidden;}}

    /* Global Background with Gold/Silver/Black Gradient */
    .stApp {{
        background: {bg_color};
        background-attachment: fixed;
        color: {text_color};
        margin-top: 0 !important;
        padding-top: 0 !important;
        min-height: 100vh;
    }}

    /* Enhanced text readability with shadows */
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6, span, div {{
        color: {text_color} !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8) !important;
    }}

    /* Main container with glass effect and top padding for fixed navbar */
    .main .block-container {{
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(15px) !important;
        border-radius: 20px !important;
        margin: 1rem !important;
        margin-top: 6rem !important;
        padding-top: 2rem !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255, 215, 0, 0.3) !important;
    }}

    /* Remove ALL Streamlit default spacing */
    .main .block-container {{
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        margin-top: 0 !important;
        max-width: 100%;
    }}

    /* Remove element container spacing */
    .stElementContainer,
    .element-container,
    [data-testid="stElementContainer"],
    [data-testid="stMarkdownContainer"],
    [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"] {{
        margin: 0 !important;
        padding: 0 !important;
        min-height: 0 !important;
        background: transparent !important;
        border: 0 !important;
    }}

    /* Remove any container spacing */
    .stApp > div:first-child {{
        padding-top: 0 !important;
        margin-top: 0 !important;
    }}

    /* Remove markdown container spacing */
    .stMarkdown, .stMarkdownWrapper, .stMarkdownContainer {{
        margin: 0 !important;
        padding: 0 !important;
    }}

    /* Remove column container spacing */
    .stColumn, [data-testid="column"] {{
        padding: 0 !important;
        margin: 0 !important;
    }}

    /* Navbar styling */
    .navbar {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 2rem;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}

    .navbar-brand {{
        font-size: 1.5rem;
        font-weight: bold;
        color: #FFD700;
        display: flex;
        align-items: center;
    }}

    .navbar-nav {{
        display: flex;
        gap: 2rem;
    }}

    .nav-link {{
        color: white;
        text-decoration: none;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        transition: all 0.3s ease;
        cursor: pointer;
    }}

    .nav-link:hover {{
        background: rgba(255, 215, 0, 0.2);
        transform: translateY(-2px);
    }}

    /* Subject card hover effects */
    .subject-card {{
        transition: all 0.3s ease;
        cursor: pointer;
    }}

    .subject-card:hover {{
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 15px 40px rgba(0,0,0,0.4) !important;
    }}

    /* Dark Mode Toggle */
    .theme-toggle {{
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        border: none;
        border-radius: 50px;
        padding: 10px 20px;
        color: white;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
        transition: all 0.3s ease;
    }}

    .theme-toggle:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
    }}

    /* Landing Page Styles */
    .landing-container {{
        text-align: center;
        padding: 0;
        margin: 0 auto;
        max-width: 1200px;
        min-height: 50vh;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: center;
        padding-top: 0;
        margin-top: 0;
    }}

    .crown-logo {{
        position: relative;
        display: inline-block;
        margin: 0 !important;
        padding: 0 !important;
        height: 100px;
        margin-top: 0 !important;
    }}

    .crown-icon {{
        font-size: 2rem;
        position: absolute;
        top: -25px;
        left: 50%;
        transform: translateX(-50%);
        color: #FFD700;
        z-index: 10;
    }}

    .brand-letter {{
        width: 70px;
        height: 70px;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        border-radius: 15px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        font-weight: 900;
        color: white;
        margin: 0 auto;
        box-shadow: 0 8px 30px rgba(255, 215, 0, 0.3);
        border: 2px solid rgba(255, 255, 255, 0.2);
        position: relative;
        z-index: 1;
    }}

    .landing-title {{
        font-size: 2.5rem;
        font-weight: 800;
        color: #FFD700;
        margin: 0.25rem 0 0.25rem 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}

    .landing-subtitle {{
        font-size: 1.1rem;
        color: {subtitle_color};
        max-width: 600px;
        margin: 0 auto 0.5rem auto;
        line-height: 1.4;
        text-align: center;
        display: block;
        width: 100%;
    }}

    /* Flash Cards - Single Row Layout */
    .flash-cards {{
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin: 4rem 0;
        flex-wrap: wrap;
        max-width: 1200px;
        margin-left: auto;
        margin-right: auto;
    }}

    .flash-card {{
        background: {card_bg};
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 1px solid rgba(255, 215, 0, 0.2);
        transition: all 0.3s ease;
        flex: 1;
        min-width: 250px;
        max-width: 280px;
        backdrop-filter: blur(10px);
    }}

    .flash-card:hover {{
        transform: translateY(-8px);
        box-shadow: 0 15px 35px rgba(255, 215, 0, 0.2);
        border-color: #FFD700;
    }}

    .flash-card-icon {{
        font-size: 3rem;
        margin-bottom: 1rem;
        color: #FFD700;
    }}

    .flash-card-title {{
        font-size: 1.3rem;
        font-weight: 600;
        color: {text_color};
        margin-bottom: 0.8rem;
    }}

    .flash-card-desc {{
        color: {subtitle_color};
        font-size: 0.95rem;
        line-height: 1.5;
    }}

    /* Sticky Navigation Bar - Full Width */
    .navbar {{
        background: linear-gradient(135deg, #FFD700, #FFA500);
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        width: 100%;
        z-index: 9999;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        backdrop-filter: blur(10px);
        border-bottom: 2px solid rgba(255, 215, 0, 0.5);
    }}

    .navbar-brand {{
        display: flex;
        align-items: center;
        font-size: 1.5rem;
        font-weight: 700;
        color: white;
        text-decoration: none;
    }}

    .navbar-nav {{
        display: flex;
        gap: 2rem;
        align-items: center;
    }}

    .nav-link {{
        color: white;
        text-decoration: none;
        font-weight: 500;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        transition: background 0.3s ease;
        cursor: pointer;
    }}

    .nav-link:hover {{
        background: rgba(255,255,255,0.2);
    }}

    .nav-link.active {{
        background: rgba(255,255,255,0.3);
    }}

    /* Centered Auth Container */
    .auth-container {{
        max-width: 450px;
        margin: 2rem auto;
        background: {card_bg};
        border-radius: 20px;
        box-shadow: 0 15px 50px rgba(0,0,0,0.15);
        overflow: hidden;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 215, 0, 0.2);
    }}

    .auth-tabs {{
        display: flex;
        background: rgba(248, 249, 250, 0.1);
    }}

    .auth-tab {{
        flex: 1;
        padding: 1rem;
        text-align: center;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        background: transparent;
        color: {text_color};
    }}

    .auth-tab.active {{
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: white;
    }}

    .auth-form {{
        padding: 2.5rem;
    }}

    /* Removed login page wrappers; keep simple centering via Streamlit columns */
    .login-header, .login-page, .login-form-container {{ display: contents; }}

    /* Math rendering and code blocks */
    .math-line {{
        font-family: 'Courier New', monospace;
        background: rgba(255,193,7,0.12);
        padding: 0.6rem 0.8rem;
        margin: 0.5rem 0;
        border-radius: 6px;
        color: #d49100;
        text-align: center;
        line-height: 1.6;
        border: 1px solid rgba(255,193,7,0.25);
    }}
    .fraction-display {{ display: inline-block; text-align: center; margin: 0 6px; vertical-align: middle; line-height: 1.2; }}
    .fraction-bar {{ border-bottom: 2px solid #d49100; margin: 2px 0; line-height: 1; width: 100%; }}
    .power {{ font-size: 0.8em; vertical-align: super; line-height: 0; }}
    .code-block {{ background: #0d1117; color: #c9d1d9; border-radius: 8px; margin: 0.75rem 0; border: 1px solid #30363d; }}
    .code-block .code-header {{ background: #161b22; color: #8b949e; font-size: 0.85rem; padding: 0.3rem 0.6rem; border-bottom: 1px solid #30363d; border-top-left-radius: 8px; border-top-right-radius: 8px; }}
    .code-block pre {{ margin: 0; padding: 0.75rem; overflow-x: auto; }}
    .step-code {{ background: rgba(0,0,0,0.04); border: 1px dashed rgba(0,0,0,0.2); padding: 0.6rem; border-radius: 6px; margin: 0.4rem 0 0.8rem 0; }}
    .final-answer {{
        background: linear-gradient(135deg, #FFD700, #FFA500) !important;
        border: 2px solid #FFD700 !important;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-radius: 8px;
        text-align: center;
        font-weight: bold;
        font-size: 1.2em;
        color: #000000 !important;
        text-shadow: none !important;
        box-shadow: 0 4px 20px rgba(255, 215, 0, 0.5) !important;
    }}

    /* Enhanced Button Styling */
    .stButton > button {{
        background: linear-gradient(45deg, #FFD700, #C0C0C0) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        text-shadow: none !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }}

    .stButton > button:hover {{
        background: linear-gradient(45deg, #FFA500, #E6E6FA) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4) !important;
    }}

    /* Enhanced Input Field Styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.95) !important;
        color: #000000 !important;
        border: 2px solid rgba(255, 215, 0, 0.4) !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
        text-shadow: none !important;
        max-width: 350px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #FFD700 !important;
        box-shadow: 0 0 12px rgba(255, 215, 0, 0.4) !important;
        outline: none !important;
    }

    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.95) !important;
        color: #000000 !important;
        border: 2px solid rgba(255, 215, 0, 0.4) !important;
        border-radius: 8px !important;
        padding: 12px 14px !important;
        font-size: 14px !important;
        text-shadow: none !important;
        max-width: 500px !important;
        min-height: 100px !important;
        max-height: 250px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        resize: vertical !important;
    }

    .stTextArea > div > div > textarea:focus {
        border-color: #FFD700 !important;
        box-shadow: 0 0 12px rgba(255, 215, 0, 0.4) !important;
        outline: none !important;
    }

    /* Enhanced Subject Cards */
    .subject-card {
        background: rgba(255, 255, 255, 0.2) !important;
        backdrop-filter: blur(15px) !important;
        border: 2px solid rgba(255, 215, 0, 0.3) !important;
        border-radius: 15px !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    .subject-card:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 40px rgba(255, 215, 0, 0.4) !important;
        background: rgba(255, 255, 255, 0.3) !important;
        border-color: #FFD700 !important;
    }

    /* Solution Content with High Contrast */
    .solution-content {
        background: rgba(255, 255, 255, 0.95) !important;
        color: #000000 !important;
        border-radius: 10px !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        border-left: 4px solid #FFD700 !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
    }

    .solution-content * {
        color: #000000 !important;
        text-shadow: none !important;
    }

    </style>
    """, unsafe_allow_html=True)

# Subject definitions
SUBJECTS = {
    "Mathematics": {
        "icon": "",
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
        "icon": "",
        "prompt": """You are a senior physics tutor. Produce highly readable, plain‑text solutions.

FORMATTING REQUIREMENTS (STRICT):
1. Use "**Step 1:**", "**Step 2:**" etc. for each step (short title on one line)
2. On the next line, briefly explain the idea (why we do this step)
3. On the next line, put the equation with quantities and units in simple text (no LaTeX, no \\(...\\) or symbols). Examples:
   - v = u + a*t
   - F = m*a
   - v = sqrt(2*g*h)
4. Substitute numbers on a separate line, with SI units:
   - v = sqrt(2*9.8 m/s^2*10 m)
5. Compute and show the numeric result on its own line with the unit:
   - v = 14.0 m/s
6. Include a short "Assumptions" line when needed (e.g., ignore air resistance).
7. End with "**Final Answer:**" on its own line with the value and the unit.

STYLE:
- Plain text only (no LaTeX, no Greek letters, write "mu" not μ)
- Keep numbers with 2–3 significant figures unless the question demands otherwise
- Always show units in every formula line and result line
- Add blank lines between steps for readability
""",
        "example": "A 2 kg object falls from 10 m height. Find velocity just before impact."
    },
    "Chemistry": {
        "icon": "",
        "prompt": """You are a senior chemistry tutor. Produce highly readable, plain‑text solutions.

FORMATTING REQUIREMENTS (STRICT):
1. Use "**Step 1:**", "**Step 2:**" etc. as a SINGLE LINE title
2. On the next line, explain the idea briefly (why this step is needed)
3. On the next line, write the relevant equation in simple text (no LaTeX). Examples:
   - rate = k * [A]^m * [B]^n
   - t_half = 0.693 / k
   - M = m / n
4. Substitute numbers on a separate line with proper units where applicable
5. Compute and show the numeric result on its own line with clear units
6. Balance chemical equations when required and show the balanced form on its own line
7. Add an "Assumptions" line when needed (e.g., ideal behavior, constant temperature)
8. End with "**Final Answer:**" on its own line with the value (and unit) or the balanced equation

STYLE:
- Plain text only (no LaTeX, avoid special symbols). Write arrows using '->' and charges like 'SO4^2-'
- Keep numbers to 2–3 significant figures unless the problem demands more
- Always include units next to numbers where relevant
- Add blank lines between steps for readability
""",
        "example": "Balance: Al + O2 -> Al2O3"
    },
    "Biology": {
        "icon": "",
        "prompt": """You are a senior biology tutor. Produce highly readable, plain‑text solutions.

FORMATTING REQUIREMENTS (STRICT):
1. Use "**Step 1:**", "**Step 2:**" etc. as a SINGLE LINE title
2. On the next line, explain the idea briefly (why this step matters biologically)
3. On the next line, if a process/equation exists, write it in simple text (no LaTeX). Examples:
   - Photosynthesis: 6 CO2 + 6 H2O -> C6H12O6 + 6 O2
   - ATP yield per glucose in aerobic respiration: ~30–32 ATP
4. If any quantities are computed, show substitution on a separate line and result on a new line with units (price/quantity)
5. Add an "Assumptions" line when needed (e.g., standard temperature, typical eukaryotic cell)
6. End with "**Final Answer:**" summarizing the key result or definition in one clear sentence

STYLE:
- Plain text only, no LaTeX; arrows as '->', charges as '^', and units explicit when used
- 2–3 concise sentences per step; add blank lines between steps for readability
""",
        "example": "Explain the process of cellular respiration in detail."
    },
    "English Literature": {
        "icon": "",
        "prompt": """You are a senior literature tutor. Produce structured, plain‑text analyses.

FORMATTING REQUIREMENTS (STRICT):
1. Use steps as SINGLE LINE titles (e.g., **Step 1:** Thesis)
2. Next line: concise explanation of the claim for that step
3. Next line: quote or evidence (short and attributed) on its own line with quotation marks
4. Next line: analysis that links evidence to the claim in 1–2 sentences
5. Repeat for 2–3 key points
6. End with "**Final Answer:**" one‑sentence conclusion that directly answers the question

STYLE:
- Plain text only; keep quotes short; add blank lines between steps for readability
""",
        "example": "Analyze the symbolism of light and darkness in Romeo and Juliet."
    },
    "History": {
        "icon": "",
        "prompt": """You are a senior history tutor. Produce chronological/thematic, plain‑text analyses.

FORMATTING REQUIREMENTS (STRICT):
1. Use steps as SINGLE LINE titles (e.g., **Step 1:** Long‑term causes)
2. Next line: 1–2 sentence explanation of the factor
3. Next line: key evidence/fact/date on its own line
4. Next line: consequence/impact that links to the question
5. Cover 3–5 major factors; keep each step compact
6. End with "**Final Answer:**" one‑sentence conclusion that synthesizes the argument

STYLE:
- Plain text only; neutral tone; add blank lines between steps for readability
""",
        "example": "Analyze the causes of World War I."
    },
    "Economics": {
        "icon": "",
        "prompt": """You are a senior economics tutor. Produce clear, plain‑text, step‑by‑step solutions.

FORMATTING REQUIREMENTS (STRICT):
1. Use "**Step 1:**", "**Step 2:**" etc. as SINGLE LINE titles
2. Next line: explain the concept (demand/supply/elasticity/etc.) in 1–2 sentences
3. Next line: write the relevant equation in simple text (no LaTeX). Examples:
   - Qd = a − bP
   - Qs = c + dP
   - Equilibrium: set Qd = Qs and solve for P and Q
4. If numbers are given, show substitution on a separate line and compute the result on a new line with units (price/quantity)
5. Add assumptions where needed (e.g., linear demand, ceteris paribus)
6. End with "**Final Answer:**" stating the numeric or conceptual result

STYLE:
- Plain text only; keep math simple and vertically separated; add blank lines between steps for readability
""",
        "example": "Explain supply and demand equilibrium with a market example."
    },
    "Computer Science": {
        "icon": "",
        "prompt": """You are a computer science expert. Provide solutions using the EXACT format below.

FORMATTING REQUIREMENTS:
1. Use "**Step 1:**", "**Step 2:**" etc. for each step as a SINGLE LINE
2. Follow each step with explanatory text on the NEXT LINE
3. Then show relevant syntax/code snippet on SEPARATE LINES (not horizontal)
4. Add blank lines between steps for readability
5. ALWAYS include "**Time Complexity:**" and "**Space Complexity:**" sections before the final code
6. End with "**Complete Code**" followed by ONE consolidated, executable code block fenced with language (e.g., ```python)
```

Follow these instructions to make the following change to my code document.

Instruction: 

Code Edit:
```
{{ ... }}
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4) !important;
    }}

    /* Enhanced Input Field Styling */
    .stTextInput > div > div > input {{
        background: rgba(255, 255, 255, 0.95) !important;
        color: #000000 !important;
        border: 2px solid rgba(255, 215, 0, 0.4) !important;
        border-radius: 8px !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
        text-shadow: none !important;
        max-width: 350px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }}

    .stTextInput > div > div > input:focus {{
        border-color: #FFD700 !important;
        box-shadow: 0 0 12px rgba(255, 215, 0, 0.4) !important;
        outline: none !important;
    }}

    .stTextArea > div > div > textarea {{
        background: rgba(255, 255, 255, 0.95) !important;
        color: #000000 !important;
        border: 2px solid rgba(255, 215, 0, 0.4) !important;
        border-radius: 8px !important;
        padding: 12px 14px !important;
        font-size: 14px !important;
        text-shadow: none !important;
        max-width: 500px !important;
        min-height: 100px !important;
        max-height: 250px !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
        resize: vertical !important;
    }}

    .stTextArea > div > div > textarea:focus {{
        border-color: #FFD700 !important;
        box-shadow: 0 0 12px rgba(255, 215, 0, 0.4) !important;
        outline: none !important;
    }}

    /* Enhanced Subject Cards */
    .subject-card {{
        background: rgba(255, 255, 255, 0.2) !important;
{{ ... }}
        backdrop-filter: blur(15px) !important;
        border: 2px solid rgba(255, 215, 0, 0.3) !important;
        border-radius: 15px !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s ease !important;
    }}

    .subject-card:hover {{
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 40px rgba(255, 215, 0, 0.4) !important;
        background: rgba(255, 255, 255, 0.3) !important;
        border-color: #FFD700 !important;
    }}

    /* Solution Content with High Contrast */
    .solution-content {{
        background: rgba(255, 255, 255, 0.95) !important;
        color: #000000 !important;
        border-radius: 10px !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        border-left: 4px solid #FFD700 !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
    }}

    .solution-content * {{
        color: #000000 !important;
        text-shadow: none !important;
    }}

    </style>
    """, unsafe_allow_html=True)

# Subject definitions
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
        "prompt": """You are a senior physics tutor. Produce highly readable, plain‑text solutions.

FORMATTING REQUIREMENTS (STRICT):
1. Use "**Step 1:**", "**Step 2:**" etc. for each step (short title on one line)
2. On the next line, briefly explain the idea (why we do this step)
3. On the next line, put the equation with quantities and units in simple text (no LaTeX, no \\(...\\) or symbols). Examples:
   - v = u + a*t
   - F = m*a
   - v = sqrt(2*g*h)
4. Substitute numbers on a separate line, with SI units:
   - v = sqrt(2*9.8 m/s^2*10 m)
5. Compute and show the numeric result on its own line with the unit:
   - v = 14.0 m/s
6. Include a short "Assumptions" line when needed (e.g., ignore air resistance).
7. End with "**Final Answer:**" on its own line with the value and the unit.

STYLE:
- Plain text only (no LaTeX, no Greek letters, write "mu" not μ)
- Keep numbers with 2–3 significant figures unless the question demands otherwise
- Always show units in every formula line and result line
- Add blank lines between steps for readability
""",
        "example": "A 2 kg object falls from 10 m height. Find velocity just before impact."
    },
    "Chemistry": {
        "icon": "🧪",
        "prompt": """You are a senior chemistry tutor. Produce highly readable, plain‑text solutions.

FORMATTING REQUIREMENTS (STRICT):
1. Use "**Step 1:**", "**Step 2:**" etc. as a SINGLE LINE title
2. On the next line, explain the idea briefly (why this step is needed)
3. On the next line, write the relevant equation in simple text (no LaTeX). Examples:
   - rate = k * [A]^m * [B]^n
   - t_half = 0.693 / k
   - M = m / n
4. Substitute numbers on a separate line with proper units where applicable
5. Compute and show the numeric result on its own line with clear units
6. Balance chemical equations when required and show the balanced form on its own line
7. Add an "Assumptions" line when needed (e.g., ideal behavior, constant temperature)
8. End with "**Final Answer:**" on its own line with the value (and unit) or the balanced equation

STYLE:
- Plain text only (no LaTeX, avoid special symbols). Write arrows using '->' and charges like 'SO4^2-'
- Keep numbers to 2–3 significant figures unless the problem demands more
- Always include units next to numbers where relevant
- Add blank lines between steps for readability
""",
        "example": "Balance: Al + O2 -> Al2O3"
    },
    "Biology": {
        "icon": "🧬",
        "prompt": """You are a senior biology tutor. Produce highly readable, plain‑text solutions.

FORMATTING REQUIREMENTS (STRICT):
1. Use "**Step 1:**", "**Step 2:**" etc. as a SINGLE LINE title
2. On the next line, explain the idea briefly (why this step matters biologically)
3. On the next line, if a process/equation exists, write it in simple text (no LaTeX). Examples:
   - Photosynthesis: 6 CO2 + 6 H2O -> C6H12O6 + 6 O2
   - ATP yield per glucose in aerobic respiration: ~30–32 ATP
4. If any quantities are computed, show substitution on a separate line and result on a new line with units
5. Add an "Assumptions" line when needed (e.g., standard temperature, typical eukaryotic cell)
6. End with "**Final Answer:**" summarizing the key result or definition in one clear sentence

STYLE:
- Plain text only, no LaTeX; arrows as '->', charges as '^', and units explicit when used
- 2–3 concise sentences per step; add blank lines between steps for readability
""",
        "example": "Explain the process of cellular respiration in detail."
    },
    "English Literature": {
        "icon": "📚",
        "prompt": """You are a senior literature tutor. Produce structured, plain‑text analyses.

FORMATTING REQUIREMENTS (STRICT):
1. Use steps as SINGLE LINE titles (e.g., **Step 1:** Thesis)
2. Next line: concise explanation of the claim for that step
3. Next line: quote or evidence (short and attributed) on its own line with quotation marks
4. Next line: analysis that links evidence to the claim in 1–2 sentences
5. Repeat for 2–3 key points
6. End with "**Final Answer:**" one‑sentence conclusion that directly answers the question

STYLE:
- Plain text only; keep quotes short; add blank lines between steps for readability
""",
        "example": "Analyze the symbolism of light and darkness in Romeo and Juliet."
    },
    "History": {
        "icon": "🏛️",
        "prompt": """You are a senior history tutor. Produce chronological/thematic, plain‑text analyses.

FORMATTING REQUIREMENTS (STRICT):
1. Use steps as SINGLE LINE titles (e.g., **Step 1:** Long‑term causes)
2. Next line: 1–2 sentence explanation of the factor
3. Next line: key evidence/fact/date on its own line
4. Next line: consequence/impact that links to the question
5. Cover 3–5 major factors; keep each step compact
6. End with "**Final Answer:**" one‑sentence conclusion that synthesizes the argument

STYLE:
- Plain text only; neutral tone; add blank lines between steps for readability
""",
        "example": "Analyze the causes of World War I."
    },
    "Economics": {
        "icon": "💰",
        "prompt": """You are a senior economics tutor. Produce clear, plain‑text, step‑by‑step solutions.

FORMATTING REQUIREMENTS (STRICT):
1. Use "**Step 1:**", "**Step 2:**" etc. as SINGLE LINE titles
2. Next line: explain the concept (demand/supply/elasticity/etc.) in 1–2 sentences
3. Next line: write the relevant equation in simple text (no LaTeX). Examples:
   - Qd = a − bP
   - Qs = c + dP
   - Equilibrium: set Qd = Qs and solve for P and Q
4. If numbers are given, show substitution on a separate line and compute the result on a new line with units (price/quantity)
5. Add assumptions where needed (e.g., linear demand, ceteris paribus)
6. End with "**Final Answer:**" stating the numeric or conceptual result

STYLE:
- Plain text only; keep math simple and vertically separated; add blank lines between steps for readability
""",
        "example": "Explain supply and demand equilibrium with a market example."
    },
    "Computer Science": {
        "icon": "💻",
        "prompt": """You are a computer science expert. Provide solutions using the EXACT format below.

FORMATTING REQUIREMENTS:
1. Use "**Step 1:**", "**Step 2:**" etc. for each step as a SINGLE LINE
2. Follow each step with explanatory text on the NEXT LINE
3. Then show relevant syntax/code snippet on SEPARATE LINES (not horizontal)
4. Add blank lines between steps for readability
5. ALWAYS include "**Time Complexity:**" and "**Space Complexity:**" sections before the final code
6. End with "**Complete Code**" followed by ONE consolidated, executable code block fenced with language (e.g., ```python)

EXAMPLE FORMAT:
**Step 1:** Initialize two pointers
Set left pointer to start and right pointer to end of array.
```
left = 0
right = len(array) - 1
```

**Step 2:** Compare middle element
Find middle index and compare with target value.
```
mid = (left + right) // 2
if array[mid] == target:
    return mid
```

**Time Complexity:** O(log n) where n is the size of the array
**Space Complexity:** O(1) constant space usage

**Complete Code**
```python
# full, runnable program here
```

Keep explanations clean and readable with proper vertical separation.""",
        "example": "Implement binary search algorithm in Python."
    }
}

# API Functions
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

    model = "openai/gpt-4o-mini"
    if subject in ("Physics", "Chemistry"):
        model = "openai/gpt-4o"

    body = {
        "model": model,
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
            json=body,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            st.error("Service temporarily unavailable. Please try again.")
            return None

    except requests.exceptions.RequestException as e:
        st.error(f"Network Error: {str(e)}")
        return None

import re
import html

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
    """Improved formatting with consistent vertical fractions and tighter spacing.

    Also formats Computer Science responses:
    - Preserves fenced code blocks in a styled container
    - Keeps non-code steps readable like math section
    """
    if not response_text:
        return ""

    # Clean up LaTeX notation to simple text but preserve fraction structure
    response_text = re.sub(r'\\sqrt\{([^}]+)\}', r'sqrt(\1)', response_text)
    response_text = re.sub(r'\\[a-zA-Z]+\{?([^}]*)\}?', r'\1', response_text)

    # Handle fenced code blocks (```lang ... ```)
    formatted_content = []
    code_block_open = False
    code_lines = []
    code_lang = None

    lines = response_text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            # Add minimal spacing between sections
            if not code_block_open:
                formatted_content.append("<br>")
            continue

        # Detect start/end of fenced code blocks
        if line.startswith('```'):
            fence = line.strip()
            if not code_block_open:
                # opening
                code_block_open = True
                code_lines = []
                code_lang = fence.strip('`').strip() or 'text'
            else:
                # closing -> render and reset
                escaped = html.escape("\n".join(code_lines))
                formatted_content.append(
                    f'<div class="code-block"><div class="code-header">{code_lang}</div><pre><code>{escaped}</code></pre></div>'
                )
                code_block_open = False
                code_lines = []
                code_lang = None
            continue

        if code_block_open:
            code_lines.append(line)
            continue

        # Skip stray closing tags that may appear in the model text
        if re.match(r'^\s*</(div|span|p)>\s*$', line):
            continue

        # One-line step headers with next-line explanation in monospace box
        if re.match(r'^\*\*Step \d+:', line) or re.match(r'^###\s*Step \d+:', line):
            step_text = re.sub(r'\*\*|###', '', line).strip()
            # Keep step title on one line
            formatted_content.append(f'<div style="color:#4CAF50;font-weight:700;margin:0.6rem 0 0.2rem 0;">{step_text}</div>')
            # The explanation for this step is expected on the next line; we wrap whatever comes next
            # by inserting an opener token that the next non-empty, non-step line will close.
            formatted_content.append('<!--STEP_CODE_NEXT-->')

        # Final answer (simple one-line box, as before)
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



        # If we previously saw a step header, wrap this first following line in step-code box
        elif formatted_content and formatted_content[-1] == '<!--STEP_CODE_NEXT-->':
            formatted_content.pop()  # remove token
            formatted_content.append(f'<div class="step-code">{html.escape(line)}</div>')

        # Mathematical expressions with equations (no fractions)
        elif ('=' in line and any(char in line for char in ['x', '+', '-', '*', '^', '(', ')'])):
            formatted_content.append(f'<div class="math-line">{format_powers(line)}</div>\n')

        # Regular text
        else:
            formatted_content.append(f"{format_powers(line)}\n")

    return ''.join(formatted_content)

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
        'illustrate', 'visualize'
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
    """Create simple, clean visualizations.

    Adds a basic geometry renderer for triangle construction tasks with
    given side lengths and the perpendicular bisector of BC.
    """
    question_lower = question.lower()

    try:
        plt.style.use('default')
        # Slightly smaller figure for generated diagrams to reduce UI footprint
        fig, ax = plt.subplots(figsize=(7, 4))
        fig.patch.set_facecolor('white')

        if subject == "Mathematics":
            # Lightweight geometry engine (shapes + graphs)
            if any(k in question_lower for k in [
                'triangle', 'abc', 'perpendicular bisector', 'bisector', 'median', 'altitude',
                'angle bisector', 'parallel', 'perpendicular', 'circle', 'circumcircle', 'incenter', 'circumcenter',
                'square', 'rectangle', 'polygon', 'semicircle', 'pentagon', 'hexagon', 'heptagon', 'octagon'
            ]):
                # ---------- Intelligent Detection Helpers ----------
                def find_len(name: str):
                    """Extract length measurements from question text"""
                    pattern = rf"{name}\s*=?\s*(\d+(?:\.\d+)?)\s*(?:cm|units?|m)?"
                    m = re.search(pattern, question, flags=re.IGNORECASE)
                    return float(m.group(1)) if m else None

                def find_angle(description: str):
                    """Extract angle measurements from question text"""
                    pattern = rf"{description}.*?(\d+(?:\.\d+)?)\s*degrees?"
                    m = re.search(pattern, question, flags=re.IGNORECASE)
                    return float(m.group(1)) if m else None

                def find_radius():
                    """Extract radius from question text"""
                    pattern = r"radius\s*=?\s*(\d+(?:\.\d+)?)\s*(?:cm|units?|m)?"
                    m = re.search(pattern, question, flags=re.IGNORECASE)
                    return float(m.group(1)) if m else None

                def detect_points():
                    """Detect point names mentioned in the question"""
                    points_mentioned = re.findall(r'\b([A-Z])\b', question)
                    return list(set(points_mentioned))  # Remove duplicates

                def midpoint(p, q):
                    return ((p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0)

                def draw_line(p, q, **kw):
                    ax.plot([p[0], q[0]], [p[1], q[1]], **kw)

                def draw_infinite_line_through(p, direction, length=20, **kw):
                    d = np.array(direction, dtype=float)
                    if np.linalg.norm(d) == 0:
                        return
                    d = d / np.linalg.norm(d)
                    p = np.array(p, dtype=float)
                    p1 = p - d * length
                    p2 = p + d * length
                    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], **kw)

                def perp(v):
                    return (-v[1], v[0])

                # ---------- Intelligent Triangle Construction ----------
                # Detect all possible side lengths mentioned
                detected_points = detect_points()
                side_lengths = {}

                # Try to find lengths for all possible sides
                for i, p1 in enumerate(detected_points):
                    for p2 in detected_points[i+1:]:
                        side_name = f"{p1}{p2}"
                        length = find_len(side_name)
                        if length:
                            side_lengths[side_name] = length

                # Check if we need a triangle
                need_triangle = (any(k in question_lower for k in ['triangle', ' abc', 'abc ', '△abc', '△ abc']) or
                               len(side_lengths) > 0 or
                               any(p in detected_points for p in ['A', 'B', 'C']))

                points = {}
                if need_triangle:
                    # Use detected measurements or defaults
                    ab = side_lengths.get('AB') or side_lengths.get('BA') or find_len('AB') or 5.0
                    bc = side_lengths.get('BC') or side_lengths.get('CB') or find_len('BC') or 6.0
                    ac = side_lengths.get('AC') or side_lengths.get('CA') or find_len('AC') or 4.0

                    # Construct triangle using circle-circle intersection
                    B = (0.0, 0.0)
                    C = (bc, 0.0)
                    # Calculate A position
                    x_a = (ab**2 - ac**2 + bc**2) / (2 * bc if bc != 0 else 1e-6)
                    y_sq = max(ab**2 - x_a**2, 0.0)
                    y_a = float(np.sqrt(y_sq))
                    A = (x_a, y_a)
                    points.update({'A': A, 'B': B, 'C': C})

                    # Draw triangle with intelligent labeling
                    stroke = '#000000'
                    draw_line(B, C, color=stroke, linewidth=2)
                    draw_line(C, A, color=stroke, linewidth=2)
                    draw_line(A, B, color=stroke, linewidth=2)
                    ax.scatter([A[0], B[0], C[0]], [A[1], B[1], C[1]], color='#000000', zorder=3)

                    # Label points based on what's mentioned in question
                    if 'A' in detected_points or 'triangle' in question_lower:
                        ax.text(A[0], A[1] + 0.2, 'A', ha='center', va='bottom', color=stroke, fontweight='bold')
                    if 'B' in detected_points or 'triangle' in question_lower:
                        ax.text(B[0], B[1] - 0.2, 'B', ha='center', va='top', color=stroke, fontweight='bold')
                    if 'C' in detected_points or 'triangle' in question_lower:
                        ax.text(C[0], C[1] - 0.2, 'C', ha='center', va='top', color=stroke, fontweight='bold')

                    # Label side lengths only if mentioned in question
                    def put_len(p, q, side_name, length):
                        if side_name in side_lengths or f"{side_name[1]}{side_name[0]}" in side_lengths:
                            mx, my = (p[0]+q[0])/2.0, (p[1]+q[1])/2.0
                            unit = 'cm' if 'cm' in question else 'units'
                            ax.text(mx, my + 0.15, f'{length} {unit}', color=stroke, ha='center', va='bottom')

                    put_len(B, C, 'BC', bc)
                    put_len(A, B, 'AB', ab)
                    put_len(A, C, 'AC', ac)

                # ---------- Constructions ----------
                # Perpendicular bisector of a segment XY (e.g., BC)
                seg_match = re.search(r'perpendicular\s+bisector\s+of\s+([A-Z])([A-Z])', question, flags=re.IGNORECASE)
                if seg_match:
                    x, y = seg_match.group(1).upper(), seg_match.group(2).upper()
                    if x in points and y in points:
                        P = points[x]; Q = points[y]
                    else:
                        # default segment on x-axis if points unknown
                        P, Q = (0.0, 0.0), (6.0, 0.0)
                    M = midpoint(P, Q)
                    dir_vec = (Q[0] - P[0], Q[1] - P[1])
                    draw_infinite_line_through(M, perp(dir_vec), linestyle='--', color='#4CAF50', linewidth=2, label=f'Perpendicular bisector of {x}{y}')

                # Angle bisector at a vertex (e.g., angle ABC)
                ang_match = re.search(r'(angle\s*)?bisector\s*(at|of)?\s*(angle\s*)?([A-Z])([A-Z])([A-Z])', question, flags=re.IGNORECASE)
                if ang_match:
                    a, b, c = ang_match.group(4).upper(), ang_match.group(5).upper(), ang_match.group(6).upper()
                    if a in points and b in points and c in points:
                        A, B, C = points[a], points[b], points[c]
                        v1 = np.array([A[0] - B[0], A[1] - B[1]], dtype=float)
                        v2 = np.array([C[0] - B[0], C[1] - B[1]], dtype=float)
                        if np.linalg.norm(v1) and np.linalg.norm(v2):
                            v1 /= np.linalg.norm(v1)
                            v2 /= np.linalg.norm(v2)
                            bis = v1 + v2
                            if np.linalg.norm(bis) == 0:
                                bis = perp(v1)
                            draw_infinite_line_through(B, bis, linestyle='--', color='#00E5FF', linewidth=2, label=f'Angle bisector at {b}')

                # Median from a vertex (e.g., median from A)
                med_match = re.search(r'median\s+(from|of)\s+([A-Z])', question, flags=re.IGNORECASE)
                if med_match and all(k in points for k in ['A', 'B', 'C']):
                    v = med_match.group(2).upper()
                    if v == 'A':
                        m = midpoint(points['B'], points['C'])
                        draw_line(points['A'], m, linestyle='--', color='#9C27B0', linewidth=2, label='Median from A')
                    elif v == 'B':
                        m = midpoint(points['A'], points['C'])
                        draw_line(points['B'], m, linestyle='--', color='#9C27B0', linewidth=2, label='Median from B')
                    elif v == 'C':
                        m = midpoint(points['A'], points['B'])
                        draw_line(points['C'], m, linestyle='--', color='#9C27B0', linewidth=2, label='Median from C')

                # Altitude from a vertex (e.g., altitude from A to BC)
                alt_match = re.search(r'altitude\s+(from)\s+([A-Z])', question, flags=re.IGNORECASE)
                if alt_match and all(k in points for k in ['A', 'B', 'C']):
                    v = alt_match.group(2).upper()
                    if v == 'A':
                        dir_bc = (points['C'][0] - points['B'][0], points['C'][1] - points['B'][1])
                        draw_infinite_line_through(points['A'], perp(dir_bc), linestyle='--', color='#FF9100', linewidth=2, label='Altitude from A')
                    elif v == 'B':
                        dir_ac = (points['C'][0] - points['A'][0], points['C'][1] - points['A'][1])
                        draw_infinite_line_through(points['B'], perp(dir_ac), linestyle='--', color='#FF9100', linewidth=2, label='Altitude from B')
                    elif v == 'C':
                        dir_ab = (points['B'][0] - points['A'][0], points['B'][1] - points['A'][1])
                        draw_infinite_line_through(points['C'], perp(dir_ab), linestyle='--', color='#FF9100', linewidth=2, label='Altitude from C')

                # Perpendicular/Parallel to a line through a given point (e.g., perpendicular to BC through A)
                through_match = re.search(r'(perpendicular|parallel)\s+to\s+([A-Z])([A-Z])\s+(through|from)\s+([A-Z])', question, flags=re.IGNORECASE)
                if through_match:
                    kind = through_match.group(1).lower()
                    x, y, p = through_match.group(2).upper(), through_match.group(3).upper(), through_match.group(5).upper()
                    if x in points and y in points and p in points:
                        base = (points[y][0] - points[x][0], points[y][1] - points[x][1])
                        direction = perp(base) if kind == 'perpendicular' else base
                        draw_infinite_line_through(points[p], direction, linestyle='--', color='#4CAF50' if kind=='perpendicular' else '#90CAF9', linewidth=2, label=f'{kind.title()} to {x}{y} through {p}')

                # Intelligent Circle Construction
                if 'circle' in question_lower:
                    # Detect radius from question
                    radius = find_radius() or 4.0

                    # Detect center point if mentioned
                    center = (0, 0)  # Default center
                    center_match = re.search(r'center\s+([A-Z])', question, flags=re.IGNORECASE)
                    if center_match:
                        center_point = center_match.group(1)
                        if center_point in points:
                            center = points[center_point]

                    # Draw circle
                    stroke = '#000000'
                    circle = plt.Circle(center, radius, fill=False, edgecolor=stroke, linewidth=2)
                    ax.add_patch(circle)

                    # Label center
                    ax.scatter([center[0]], [center[1]], color=stroke, s=30, zorder=3)
                    center_label = center_match.group(1) if center_match else 'O'
                    ax.text(center[0], center[1] + 0.3, center_label, ha='center', va='bottom', color=stroke, fontweight='bold')

                    # Show radius if mentioned in question
                    if find_radius() or 'radius' in question_lower:
                        ax.plot([center[0], center[0] + radius], [center[1], center[1]], color=stroke, linestyle='--', linewidth=1.5)
                        unit = 'cm' if 'cm' in question else 'units'
                        ax.text(center[0] + radius/2, center[1] + 0.2, f'r = {radius} {unit}', ha='center', va='bottom', color=stroke)

                    # Set bounds
                    ax.set_xlim(center[0] - radius - 1, center[0] + radius + 1)
                    ax.set_ylim(center[1] - radius - 1, center[1] + radius + 1)
                    ax.set_aspect('equal')

                # Improved pair of tangents to a circle with given angle between them
                tan_match = re.search(r'tangents?\s+to\s+a?\s*circle.*?(?:inclined.*?at|angle.*?of)\s*(\d+(?:\.\d+)?)\s*degrees?', question, flags=re.IGNORECASE)
                if tan_match:
                    tangent_angle = float(tan_match.group(1))  # degrees between tangents

                    # Get radius from existing circle or default
                    r = 3.0
                    center = (0.0, 0.0)
                    existing_circle = next((p for p in ax.patches if isinstance(p, plt.Circle)), None)
                    if existing_circle:
                        center = existing_circle.get_center()
                        r = existing_circle.get_radius()
                    else:
                        # Create circle if none exists
                        circle = plt.Circle(center, r, fill=False, edgecolor='#000000', linewidth=2)
                        ax.add_patch(circle)
                        ax.scatter([center[0]], [center[1]], color='#000000')
                        ax.text(center[0], center[1]+0.2, 'O', color='#000000', ha='center')

                    # Calculate central angle (supplementary to tangent angle)
                    central_angle = 180 - tangent_angle
                    A_angle = np.radians(central_angle / 2)
                    B_angle = -A_angle

                    # Points of tangency A and B
                    A = (center[0] + r * np.cos(A_angle), center[1] + r * np.sin(A_angle))
                    B = (center[0] + r * np.cos(B_angle), center[1] + r * np.sin(B_angle))

                    # Draw radii to points of tangency
                    ax.plot([center[0], A[0]], [center[1], A[1]], 'k--', linewidth=1, alpha=0.7, label='Radii')
                    ax.plot([center[0], B[0]], [center[1], B[1]], 'k--', linewidth=1, alpha=0.7)

                    # Mark points of tangency
                    ax.scatter([A[0], B[0]], [A[1], B[1]], color='red', s=30, zorder=5)
                    ax.text(A[0], A[1]+0.2, 'A', color='red', ha='center', fontweight='bold')
                    ax.text(B[0], B[1]-0.2, 'B', color='red', ha='center', fontweight='bold')

                    # Draw tangent lines (perpendicular to radii at A and B)
                    line_length = r * 3
                    for point, angle in [(A, A_angle), (B, B_angle)]:
                        # Tangent slope is perpendicular to radius
                        if np.abs(np.cos(angle)) < 1e-10:  # vertical radius
                            # Horizontal tangent
                            x_vals = np.array([point[0] - line_length, point[0] + line_length])
                            y_vals = np.array([point[1], point[1]])
                        else:
                            slope = -1 / np.tan(angle)
                            x_vals = np.array([point[0] - line_length, point[0] + line_length])
                            y_vals = slope * (x_vals - point[0]) + point[1]
                        ax.plot(x_vals, y_vals, 'red', linewidth=2, label='Tangents' if point == A else '')

                    # Mark the angle between tangents
                    ax.text(center[0], center[1]-r-0.5, f'Angle between tangents: {int(tangent_angle)}°',
                           color='#000000', ha='center', fontweight='bold')

                # Dynamic angle detection and construction
                angle_matches = re.findall(r'(\d+(?:\.\d+)?)\s*degrees?', question, flags=re.IGNORECASE)
                if angle_matches and any(word in question_lower for word in ['construct', 'draw', 'angle']):
                    for angle_str in angle_matches:
                        angle_deg = float(angle_str)

                        # Intelligent construction based on the angle
                        stroke = '#000000'

                        # Base line (horizontal)
                        ax.plot([-2, 4], [0, 0], color=stroke, linewidth=2, label='Base line')

                        # Vertex point
                        vertex = (0, 0)
                        ax.scatter([vertex[0]], [vertex[1]], color=stroke, s=50, zorder=5)
                        ax.text(vertex[0]-0.2, vertex[1]-0.3, 'O', color=stroke, ha='center', fontweight='bold')

                        # Construct the angle
                        angle_rad = np.radians(angle_deg)
                        end_point = (3 * np.cos(angle_rad), 3 * np.sin(angle_rad))

                        # Draw the angle ray
                        ax.plot([vertex[0], end_point[0]], [vertex[1], end_point[1]], color='red', linewidth=2, label=f'{angle_deg}° ray')

                        # Mark the angle arc
                        arc_radius = 1.0
                        arc_angles = np.linspace(0, angle_rad, 50)
                        arc_x = vertex[0] + arc_radius * np.cos(arc_angles)
                        arc_y = vertex[1] + arc_radius * np.sin(arc_angles)
                        ax.plot(arc_x, arc_y, color='blue', linewidth=2, label='Angle arc')

                        # Label the angle
                        label_angle = angle_rad / 2
                        label_x = vertex[0] + (arc_radius + 0.3) * np.cos(label_angle)
                        label_y = vertex[1] + (arc_radius + 0.3) * np.sin(label_angle)
                        ax.text(label_x, label_y, f'{angle_deg}°', color='blue', ha='center', fontweight='bold')

                        # Show construction method for special angles
                        if abs(angle_deg - 60) < 1:
                            # Equilateral triangle construction for 60°
                            circle1 = plt.Circle(vertex, 2, fill=False, edgecolor='green', linewidth=1, linestyle='--', alpha=0.7)
                            circle2 = plt.Circle((2, 0), 2, fill=False, edgecolor='green', linewidth=1, linestyle='--', alpha=0.7)
                            ax.add_patch(circle1)
                            ax.add_patch(circle2)
                            ax.text(1, -2.5, 'Construction: Equilateral triangle method', color='green', ha='center', fontsize=10)
                        elif abs(angle_deg - 90) < 1:
                            # Right angle construction
                            ax.text(1, -2.5, 'Construction: Perpendicular lines', color='green', ha='center', fontsize=10)
                        elif abs(angle_deg - 45) < 1:
                            # 45° angle construction
                            ax.text(1, -2.5, 'Construction: Angle bisector of 90°', color='green', ha='center', fontsize=10)

                        # Set appropriate bounds
                        ax.set_xlim(-2.5, 4.5)
                        ax.set_ylim(-3, 3)
                        ax.set_aspect('equal')
                        break  # Only construct the first angle found

                # Final styling and bounds
                ax.set_aspect('equal', adjustable='datalim')

                # PRIORITIZE CIRCLE-FRIENDLY BOUNDS
                # If a circle exists, frame the view around it so it is always clearly visible.
                circ = next((p for p in ax.patches if isinstance(p, plt.Circle)), None)
                if circ is not None:
                    c = circ.get_center(); r = circ.get_radius()
                    pad = max(0.4 * r, 1.0)
                    ax.set_xlim(c[0] - r - pad, c[0] + r + pad)
                    ax.set_ylim(c[1] - r - pad, c[1] + r + pad)
                else:
                    # Generic autoscaling when no circle is present
                    x_all, y_all = [], []
                    # Lines
                    for line in ax.get_lines():
                        xdata = line.get_xdata(); ydata = line.get_ydata()
                        x_all.extend(list(xdata)); y_all.extend(list(ydata))
                    if x_all and y_all:
                        x_min, x_max = min(x_all), max(x_all)
                        y_min, y_max = min(y_all), max(y_all)
                        pad_x = max((x_max - x_min) * 0.15, 1.0)
                        pad_y = max((y_max - y_min) * 0.15, 1.0)
                        ax.set_xlim(x_min - pad_x, x_max + pad_x)
                        ax.set_ylim(y_min - pad_y, y_max + pad_y)
                    else:
                        # Safe default frame
                        ax.set_xlim(-5, 5)
                        ax.set_ylim(-5, 5)
                ax.axis('off')
                ax.legend(loc='upper right')
            else:
                # Existing math plots
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
            # Intelligent Physics diagram detection
            question_lower = question.lower()

            # Wave motion detection
            if any(term in question_lower for term in ['wave', 'frequency', 'amplitude', 'wavelength', 'oscillation']):
                # Extract wave parameters
                freq_match = re.search(r'frequency.*?(\d+(?:\.\d+)?)', question, flags=re.IGNORECASE)
                amp_match = re.search(r'amplitude.*?(\d+(?:\.\d+)?)', question, flags=re.IGNORECASE)

                freq = float(freq_match.group(1)) if freq_match else 1.0
                amp = float(amp_match.group(1)) if amp_match else 1.0

                t = np.linspace(0, 4*np.pi/freq, 1000)
                y = amp * np.sin(freq * t)
                ax.plot(t, y, 'b-', linewidth=2, label=f'Wave (f={freq}Hz, A={amp})')
                ax.set_title('Wave Motion')
                ax.set_xlabel('Time (s)')
                ax.set_ylabel('Amplitude')
                ax.grid(True, alpha=0.3)
                ax.axhline(y=0, color='k', linewidth=0.5)
                ax.legend()

            # Circuit diagram detection
            elif any(term in question_lower for term in ['circuit', 'resistor', 'voltage', 'current', 'ohm']):
                # Simple circuit representation
                ax.plot([0, 2, 2, 0, 0], [0, 0, 1, 1, 0], 'k-', linewidth=2, label='Circuit')
                ax.plot([0.5, 1.5], [0.5, 0.5], 'k-', linewidth=3, label='Resistor')
                ax.text(1, 0.7, 'R', ha='center', fontweight='bold')
                ax.text(1, -0.2, 'Circuit Diagram', ha='center', fontweight='bold')
                ax.set_xlim(-0.5, 2.5)
                ax.set_ylim(-0.5, 1.5)
                ax.set_aspect('equal')
                ax.axis('off')

            # Motion/trajectory detection
            elif any(term in question_lower for term in ['motion', 'trajectory', 'projectile', 'velocity', 'acceleration']):
                # Extract motion parameters
                vel_match = re.search(r'velocity.*?(\d+(?:\.\d+)?)', question, flags=re.IGNORECASE)
                angle_match = re.search(r'angle.*?(\d+(?:\.\d+)?)', question, flags=re.IGNORECASE)

                v0 = float(vel_match.group(1)) if vel_match else 20
                angle = float(angle_match.group(1)) if angle_match else 45

                g = 9.8
                angle_rad = np.radians(angle)
                t_max = 2 * v0 * np.sin(angle_rad) / g
                t = np.linspace(0, t_max, 100)
                x = v0 * np.cos(angle_rad) * t
                y = v0 * np.sin(angle_rad) * t - 0.5 * g * t**2

                ax.plot(x, y, 'r-', linewidth=2, label=f'Trajectory (v₀={v0}m/s, θ={angle}°)')
                ax.set_title('Projectile Motion')
                ax.set_xlabel('Horizontal Distance (m)')
                ax.set_ylabel('Height (m)')
                ax.grid(True, alpha=0.3)
                ax.legend()

            else:
                # Default wave
                t = np.linspace(0, 4*np.pi, 100)
                y = np.sin(t)
                ax.plot(t, y, 'b-', linewidth=2, label='Wave')
                ax.set_title('Wave Function')
                ax.set_xlabel('Time/Position')
                ax.set_ylabel('Amplitude')
                ax.grid(True, alpha=0.3)
                ax.legend()

        elif subject == "Economics":
            # Intelligent Economics diagram detection
            question_lower = question.lower()

            # Supply and demand detection
            if any(term in question_lower for term in ['supply', 'demand', 'equilibrium', 'market']):
                # Extract economic parameters
                price_match = re.search(r'price.*?(\d+(?:\.\d+)?)', question, flags=re.IGNORECASE)
                quantity_match = re.search(r'quantity.*?(\d+(?:\.\d+)?)', question, flags=re.IGNORECASE)

                max_q = float(quantity_match.group(1)) if quantity_match else 10
                max_p = float(price_match.group(1)) if price_match else 20

                x = np.linspace(0, max_q, 100)
                supply = (max_p / max_q) * x  # Linear supply
                demand = max_p - (max_p / max_q) * x  # Linear demand

                ax.plot(x, supply, 'b-', linewidth=2, label='Supply')
                ax.plot(x, demand, 'r-', linewidth=2, label='Demand')

                # Find equilibrium
                eq_q = max_q / 2
                eq_p = max_p / 2
                ax.plot(eq_q, eq_p, 'go', markersize=8, label=f'Equilibrium (Q={eq_q}, P={eq_p})')
                ax.axhline(y=eq_p, color='gray', linestyle='--', alpha=0.5)
                ax.axvline(x=eq_q, color='gray', linestyle='--', alpha=0.5)

                ax.set_title('Supply and Demand')
                ax.set_xlabel('Quantity')
                ax.set_ylabel('Price')
                ax.grid(True, alpha=0.3)
                ax.legend()

            # Cost curves detection
            elif any(term in question_lower for term in ['cost', 'marginal', 'average', 'production']):
                x = np.linspace(1, 10, 100)
                mc = 2 * x  # Marginal cost
                ac = x + 10/x  # Average cost (U-shaped)

                ax.plot(x, mc, 'r-', linewidth=2, label='Marginal Cost')
                ax.plot(x, ac, 'b-', linewidth=2, label='Average Cost')
                ax.set_title('Cost Curves')
                ax.set_xlabel('Quantity')
                ax.set_ylabel('Cost')
                ax.grid(True, alpha=0.3)
                ax.legend()

            else:
                # Default supply and demand
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

        elif subject == "Chemistry":
            # Intelligent Chemistry diagram detection
            question_lower = question.lower()

            # Molecular structure detection
            if any(term in question_lower for term in ['molecule', 'bond', 'structure', 'lewis', 'electron']):
                # Simple molecular representation
                ax.scatter([0, 1, 2], [0, 0.5, 0], s=200, c=['red', 'blue', 'red'], alpha=0.7)
                ax.plot([0, 1], [0, 0.5], 'k-', linewidth=2)
                ax.plot([1, 2], [0.5, 0], 'k-', linewidth=2)
                ax.text(0, -0.2, 'O', ha='center', fontweight='bold', fontsize=12)
                ax.text(1, 0.7, 'C', ha='center', fontweight='bold', fontsize=12)
                ax.text(2, -0.2, 'O', ha='center', fontweight='bold', fontsize=12)
                ax.set_title('Molecular Structure')
                ax.set_xlim(-0.5, 2.5)
                ax.set_ylim(-0.5, 1)
                ax.axis('off')

            # Reaction kinetics detection
            elif any(term in question_lower for term in ['reaction', 'rate', 'kinetics', 'concentration']):
                t = np.linspace(0, 10, 100)
                conc_A = np.exp(-0.5 * t)  # First-order decay
                conc_B = 1 - np.exp(-0.5 * t)  # Product formation

                ax.plot(t, conc_A, 'r-', linewidth=2, label='Reactant A')
                ax.plot(t, conc_B, 'b-', linewidth=2, label='Product B')
                ax.set_title('Reaction Kinetics')
                ax.set_xlabel('Time')
                ax.set_ylabel('Concentration')
                ax.grid(True, alpha=0.3)
                ax.legend()

            # pH curve detection
            elif any(term in question_lower for term in ['ph', 'titration', 'acid', 'base']):
                volume = np.linspace(0, 50, 100)
                ph = 3 + 8 / (1 + np.exp(-(volume - 25) * 0.5))  # Sigmoid curve

                ax.plot(volume, ph, 'purple', linewidth=2, label='pH vs Volume')
                ax.axhline(y=7, color='gray', linestyle='--', alpha=0.5, label='Neutral pH')
                ax.set_title('Titration Curve')
                ax.set_xlabel('Volume of Titrant (mL)')
                ax.set_ylabel('pH')
                ax.grid(True, alpha=0.3)
                ax.legend()

            else:
                # Default molecular diagram
                ax.text(0.5, 0.5, 'Chemical Structure\nDiagram', ha='center', va='center',
                       fontsize=14, fontweight='bold', transform=ax.transAxes)
                ax.axis('off')

        elif subject == "Biology":
            # Intelligent Biology diagram detection
            question_lower = question.lower()

            # Cell structure detection
            if any(term in question_lower for term in ['cell', 'membrane', 'nucleus', 'organelle']):
                # Simple cell diagram
                cell = plt.Circle((0.5, 0.5), 0.4, fill=False, edgecolor='black', linewidth=2)
                nucleus = plt.Circle((0.5, 0.5), 0.15, fill=True, facecolor='lightblue', edgecolor='blue')
                ax.add_patch(cell)
                ax.add_patch(nucleus)
                ax.text(0.5, 0.5, 'Nucleus', ha='center', va='center', fontsize=8)
                ax.text(0.5, 0.1, 'Cell Membrane', ha='center', fontweight='bold')
                ax.set_title('Cell Structure')
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.set_aspect('equal')
                ax.axis('off')

            # Population growth detection
            elif any(term in question_lower for term in ['population', 'growth', 'exponential', 'logistic']):
                t = np.linspace(0, 10, 100)

                if 'logistic' in question_lower:
                    # Logistic growth
                    K = 1000  # Carrying capacity
                    r = 0.5   # Growth rate
                    N0 = 10   # Initial population
                    N = K / (1 + ((K - N0) / N0) * np.exp(-r * t))
                    ax.plot(t, N, 'g-', linewidth=2, label='Logistic Growth')
                    ax.axhline(y=K, color='red', linestyle='--', alpha=0.7, label='Carrying Capacity')
                else:
                    # Exponential growth
                    N = 10 * np.exp(0.3 * t)
                    ax.plot(t, N, 'g-', linewidth=2, label='Exponential Growth')

                ax.set_title('Population Growth')
                ax.set_xlabel('Time')
                ax.set_ylabel('Population Size')
                ax.grid(True, alpha=0.3)
                ax.legend()

            # DNA/genetics detection
            elif any(term in question_lower for term in ['dna', 'gene', 'chromosome', 'helix']):
                # Simple DNA helix representation
                t = np.linspace(0, 4*np.pi, 100)
                x1 = np.cos(t)
                y1 = t
                x2 = np.cos(t + np.pi)
                y2 = t

                ax.plot(x1, y1, 'b-', linewidth=2, label='DNA Strand 1')
                ax.plot(x2, y2, 'r-', linewidth=2, label='DNA Strand 2')

                # Base pairs
                for i in range(0, len(t), 10):
                    ax.plot([x1[i], x2[i]], [y1[i], y2[i]], 'k-', alpha=0.5, linewidth=1)

                ax.set_title('DNA Double Helix')
                ax.set_xlabel('X')
                ax.set_ylabel('Y')
                ax.legend()

            else:
                # Default biological diagram
                ax.text(0.5, 0.5, 'Biological\nDiagram', ha='center', va='center',
                       fontsize=14, fontweight='bold', transform=ax.transAxes)
                ax.axis('off')

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        return buf

    except Exception:
        plt.close('all')
        return None

# ---------------------------
# Backend helpers (HTTP)
# ---------------------------
try:
    BACKEND_URL = st.secrets.get('BACKEND_URL', 'http://127.0.0.1:8000')
except:
    BACKEND_URL = 'http://127.0.0.1:8000'

def backend_register(username: str, password: str) -> tuple[bool, str]:
    try:
        r = requests.post(f"{BACKEND_URL}/auth/register", json={"username": username, "password": password}, timeout=6)
        if r.status_code in (200, 201):
            return True, r.json().get('message', 'Account created')
        # Attempt to read common error message
        try:
            return False, r.json().get('detail', r.text)
        except Exception:
            return False, r.text
    except requests.RequestException as e:
        return False, str(e)

def backend_login(username: str, password: str) -> tuple[bool, str]:
    try:
        # backend expects form data for OAuth2PasswordRequestForm
        r = requests.post(f"{BACKEND_URL}/auth/login", data={"username": username, "password": password}, timeout=6)
        if r.status_code == 200:
            return True, r.json().get('access_token')
        try:
            return False, r.json().get('detail', r.text)
        except Exception:
            return False, r.text
    except requests.RequestException as e:
        return False, str(e)

def backend_get_me(token: str) -> tuple[bool, dict | str]:
    try:
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(f"{BACKEND_URL}/auth/me", headers=headers, timeout=6)
        if r.status_code == 200:
            return True, r.json()
        try:
            return False, r.json().get('detail', r.text)
        except Exception:
            return False, r.text
    except requests.RequestException as e:
        return False, str(e)

def backend_save_history(subject: str, question: str, answer: str) -> bool:
    """Save question/answer to backend history"""
    try:
        token = st.session_state.get("access_token")
        if not token:
            return False

        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "subject": subject,
            "question": question,
            "answer": answer
        }
        r = requests.post(f"{BACKEND_URL}/history/save", json=data, headers=headers, timeout=6)
        return r.status_code in (200, 201)
    except:
        return False

def backend_get_history(limit: int = 20, subject: str = None) -> list:
    """Get user history from backend, optionally filtered by subject"""
    try:
        token = st.session_state.get("access_token")
        if not token:
            return []

        headers = {"Authorization": f"Bearer {token}"}
        url = f"{BACKEND_URL}/history?limit={limit}"
        if subject:
            url += f"&subject={subject}"
        r = requests.get(url, headers=headers, timeout=6)
        if r.status_code == 200:
            data = r.json()
            return data.get("history", [])
        return []
    except:
        return []

# ---------------------------
# Local Database helpers (SQLite)
# ---------------------------
import sqlite3

DB_PATH = "homework_history.db"

def init_db():
    """Initialize the database with required tables"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            # Users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # History table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    subject TEXT NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            conn.commit()
    except sqlite3.Error:
        pass

def save_history(user_id: int, subject: str, question: str, answer: str):
    """Save question/answer to local database"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO history (user_id, subject, question, answer) VALUES (?, ?, ?, ?)",
                (user_id, subject, question, answer)
            )
            conn.commit()
    except sqlite3.Error:
        pass

def load_history(user_id: int, limit: int = 20, subject: str = None) -> list[tuple]:
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            if subject:
                cur.execute(
                    """
                    SELECT id, subject, question, answer, created_at
                    FROM history
                    WHERE user_id=? AND subject=?
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (user_id, subject, limit),
                )
            else:
                cur.execute(
                    """
                    SELECT id, subject, question, answer, created_at
                    FROM history
                    WHERE user_id=?
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (user_id, limit),
                )
            return cur.fetchall()
    except sqlite3.Error:
        return []

# Theme Toggle Component - REMOVED

# Page Components
def render_navbar():
    """Render horizontal navigation bar with integrated nav items"""
    st.markdown("""
    <style>
    /* Remove Streamlit's default padding */
    .main > div {
        padding-top: 0rem !important;
    }
    .block-container {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    header[data-testid="stHeader"] {
        display: none;
    }
    .stApp > header {
        display: none;
    }

    .top-navbar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0.8rem 1rem;
        margin: -1rem -1rem 1rem -1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        position: sticky;
        top: 0;
        z-index: 1000;
    }
    .navbar-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1200px;
        margin: 0 auto;
    }
    .navbar-brand {
        display: flex;
        align-items: center;
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
    }
    .navbar-nav {
        display: flex;
        gap: 1.5rem;
        align-items: center;
    }
    .nav-item {
        color: white;
        text-decoration: none;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        transition: all 0.3s ease;
        cursor: pointer;
        border: 1px solid transparent;
        background: rgba(255,255,255,0.1);
    }
    .nav-item:hover {
        background: rgba(255,255,255,0.2);
        border-color: rgba(255,255,255,0.3);
        transform: translateY(-2px);
    }
    .nav-item.active {
        background: rgba(255,215,0,0.3);
        border-color: #FFD700;
    }
    @media (max-width: 768px) {
        .navbar-nav {
            gap: 0.5rem;
        }
        .nav-item {
            padding: 0.3rem 0.6rem;
            font-size: 0.9rem;
        }
        .navbar-brand {
            font-size: 1.2rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # Create navbar with embedded navigation
    current_page = st.session_state.get('page', 'landing')

    navbar_html = f"""
    <div class="top-navbar">
        <div class="navbar-content">
            <div class="navbar-brand">
                <span style="margin-right: 10px;">👑</span>
                <span style="color: #FFD700;">EduLLM</span>
            </div>
            <div class="navbar-nav">
                <div class="nav-item {'active' if current_page == 'landing' else ''}" onclick="window.parent.postMessage({{type: 'nav', page: 'landing'}}, '*')">
                    🏠 Home
                </div>
                <div class="nav-item {'active' if current_page == 'subjects' else ''}" onclick="window.parent.postMessage({{type: 'nav', page: 'subjects'}}, '*')">
                    📚 Subjects
                </div>
                <div class="nav-item {'active' if current_page == 'profile' else ''}" onclick="window.parent.postMessage({{type: 'nav', page: 'profile'}}, '*')">
                    👤 Profile
                </div>
                <div class="nav-item {'active' if current_page == 'about' else ''}" onclick="window.parent.postMessage({{type: 'nav', page: 'about'}}, '*')">
                    ℹ️ About
                </div>
                <div class="nav-item" onclick="window.parent.postMessage({{type: 'nav', page: 'logout'}}, '*')">
                    🚪 Logout
                </div>
            </div>
        </div>
    </div>
    """

    st.markdown(navbar_html, unsafe_allow_html=True)

def render_hamburger_navbar():
    """Render hamburger menu for questions page - EduLLM left, burger right"""
    # Initialize menu state
    if 'menu_open' not in st.session_state:
        st.session_state.menu_open = False

    st.markdown("""
    <style>
    /* Remove Streamlit's default padding */
    .main > div {
        padding-top: 0rem !important;
    }
    .block-container {
        padding-top: 0rem !important;
        margin-top: 0rem !important;
    }
    header[data-testid="stHeader"] {
        display: none;
    }
    .stApp > header {
        display: none;
    }

    /* Top navigation bar */
    .questions-navbar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 2rem;
        margin: -1rem -1rem 1rem -1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        position: sticky;
        top: 0;
        z-index: 1000;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .navbar-brand {
        display: flex;
        align-items: center;
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
    }

    .hamburger-btn {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 8px;
        padding: 0.6rem 0.8rem;
        color: white;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 1.2rem;
        backdrop-filter: blur(10px);
    }
    .hamburger-btn:hover {
        background: rgba(255,255,255,0.2);
        border-color: rgba(255,255,255,0.4);
        transform: scale(1.05);
    }
    </style>
    """, unsafe_allow_html=True)

    # Top navbar with EduLLM left and hamburger right
    menu_icon = "✕" if st.session_state.menu_open else "☰"
    navbar_html = f"""
    <div class="questions-navbar">
        <div class="navbar-brand">
            <span style="margin-right: 10px;">👑</span>
            <span style="color: #FFD700;">EduLLM</span>
        </div>
        <div class="hamburger-btn">{menu_icon}</div>
    </div>
    """

    st.markdown(navbar_html, unsafe_allow_html=True)

    # Hamburger menu toggle button (invisible but functional)
    col1, col2, col3 = st.columns([8, 1, 1])
    with col3:
        if st.button(menu_icon, key="hamburger_toggle", help="Menu"):
            st.session_state.menu_open = not st.session_state.menu_open
            st.rerun()

    # Menu items at bottom when open
    if st.session_state.menu_open:
        st.markdown("---")
        st.markdown("### Navigation")

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            if st.button("✕", key="close_btn", help="Close", use_container_width=True):
                st.session_state.menu_open = False
                st.rerun()

        with col2:
            if st.button("🏠 Home", key="ham_home", use_container_width=True):
                st.session_state.page = 'landing'
                st.session_state.menu_open = False
                st.rerun()

        with col3:
            if st.button("📚 Subjects", key="ham_subjects", use_container_width=True):
                st.session_state.page = 'subjects'
                st.session_state.selected_subject = None
                st.session_state.menu_open = False
                st.rerun()

        with col4:
            if st.button("📞 Contact", key="ham_contact", use_container_width=True):
                st.session_state.page = 'about'
                st.session_state.menu_open = False
                st.rerun()

        with col5:
            if st.button("🚪 Logout", key="ham_logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.page = 'landing'
                st.session_state.menu_open = False
                st.rerun()

def render_landing_page():
    """Professional landing page with crown logo"""
    # No theme toggle on landing page for cleaner look

    st.markdown("""
    <div class="landing-container">
        <div style="text-align: center; width: 100%;">
            <div class="crown-logo">
                <div class="crown-icon">👑</div>
                <div class="brand-letter">E</div>
            </div>
            <h1 class="landing-title">EduLLM</h1>
            <div style="text-align: center; width: 100%; display: flex; justify-content: center;">
                <p class="landing-subtitle">
                    Your AI-powered homework companion. Get instant, accurate answers
                    to your school questions using cutting-edge Large Language Model
                    technology.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Start Learning Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button('🚀 Start Learning', type='primary', use_container_width=True, key='start_learning'):
            st.session_state.page = 'login'
            st.rerun()

    # Why Choose EduLLM Section
    st.markdown("""
    <div style="text-align: center; margin: 1rem 0 0.5rem 0;">
        <h2 style="font-size: 2rem; font-weight: 700; color: #333; margin-bottom: 0.5rem;">
            Why Choose <span style="color: #FFD700;">EduLLM?</span>
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # Flash Cards in Single Row
    st.markdown("""
    <div class="flash-cards">
        <div class="flash-card">
            <div class="flash-card-icon">🧠</div>
            <div class="flash-card-title">AI-Powered Learning</div>
            <div class="flash-card-desc">Advanced LLM technology helps you understand complex concepts with personalized explanations.</div>
        </div>
        <div class="flash-card">
            <div class="flash-card-icon">📖</div>
            <div class="flash-card-title">Multiple Subjects</div>
            <div class="flash-card-desc">Get help with Math, Science, History, English, and more - all in one platform.</div>
        </div>
        <div class="flash-card">
            <div class="flash-card-icon">💡</div>
            <div class="flash-card-title">Instant Solutions</div>
            <div class="flash-card-desc">Get step-by-step solutions to your homework problems in seconds.</div>
        </div>
        <div class="flash-card">
            <div class="flash-card-icon">👥</div>
            <div class="flash-card-title">Student Community</div>
            <div class="flash-card-desc">Join thousands of students who are already improving their grades with EduLLM.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Ready to Ace Section
    st.markdown("""
    <div style="text-align: center; margin: 1rem 0 0.5rem 0; padding: 1rem 0.5rem; background: rgba(255, 215, 0, 0.1); border-radius: 15px;">
        <h2 style="font-size: 2rem; font-weight: 700; color: #333; margin-bottom: 1rem;">
            Ready to Ace Your Homework?
        </h2>
        <p style="font-size: 1.1rem; color: #666; max-width: 600px; margin: 0 auto;">
            Join thousands of students who are already using EduLLM to improve their understanding and grades.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Final CTA
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button('🎯 Get Started Today', type='primary', use_container_width=True, key='get_started'):
            st.session_state.page = 'login'
            st.rerun()

def render_login_page():
    """Professional centered login/register page"""
    # No theme toggle on login page for cleaner look

    # Centered login container (removed unnecessary outer wrapper)

    # Crown logo and title - more compact
    st.markdown("""
    <div class="crown-logo" style="margin-bottom: 1rem;">
        <div class="crown-icon">👑</div>
        <div class="brand-letter" style="width: 80px; height: 80px; font-size: 2.5rem;">E</div>
    </div>
    <h1 style="font-size: 2rem; font-weight: 700; color: #FFD700; margin: 1rem 0;">Welcome to EduLLM</h1>
    """, unsafe_allow_html=True)

    # Centered auth container (removed unnecessary wrapper)
    col1, col2, col3 = st.columns([0.5, 2, 0.5])
    with col2:
        # Tabs
        tab_col1, tab_col2 = st.columns(2)
        with tab_col1:
            if st.button("Login", use_container_width=True, key="login_tab",
                        type="primary" if st.session_state.auth_tab == 'login' else "secondary"):
                st.session_state.auth_tab = 'login'
        with tab_col2:
            if st.button("Sign Up", use_container_width=True, key="register_tab",
                        type="primary" if st.session_state.auth_tab == 'register' else "secondary"):
                st.session_state.auth_tab = 'register'

        st.markdown("---")

        if st.session_state.auth_tab == 'login':
            st.markdown("### Sign In")
            st.markdown("*Enter your credentials to access your account*")
            st.markdown("")

            email = st.text_input("Email", placeholder="student@example.com", key="login_email")
            password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")

            st.markdown("")
            if st.button("Sign In", type="primary", use_container_width=True):
                if email and password:
                    # Try backend authentication first
                    try:
                        from app.backend import backend_login, backend_get_me
                        ok, token_or_err = backend_login(email, password)
                        if ok:
                            token = token_or_err
                            st.session_state["access_token"] = token
                            ok2, me_or_err = backend_get_me(token)
                            if ok2:
                                st.session_state["user_id"] = me_or_err.get("id")
                                st.session_state["username"] = me_or_err.get("username")
                                st.session_state.logged_in = True
                                st.session_state.page = 'subjects'
                                st.success("Login successful!")
                                st.rerun()
                            else:
                                st.error(f"Login succeeded but fetching user failed: {me_or_err}")
                        else:
                            st.error(f"Login failed: {token_or_err}")
                    except Exception as e:
                        # Fallback to simple login for demo
                        st.session_state.logged_in = True
                        st.session_state.user_id = abs(hash(email)) % 1000000
                        st.session_state.user_email = email
                        st.session_state.page = 'subjects'
                        st.success("Login successful (demo mode)!")
                        st.rerun()
                else:
                    st.error("Please fill in all fields")

            st.markdown("---")
            st.markdown("**OR CONTINUE WITH**")

            google_col, github_col = st.columns(2)
            with google_col:
                if st.button("🔍 Google", use_container_width=True):
                    st.info("Google login coming soon!")
            with github_col:
                if st.button("🐙 GitHub", use_container_width=True):
                    st.info("GitHub login coming soon!")

        else:  # register
            st.markdown("### Create Account")
            st.markdown("*Join thousands of students improving their grades*")
            st.markdown("")

            name = st.text_input("Full Name", placeholder="Enter your full name", key="reg_name")
            email = st.text_input("Email", placeholder="student@example.com", key="reg_email")
            password = st.text_input("Password", type="password", placeholder="Create a password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="reg_confirm")

            st.markdown("")
            if st.button("Create Account", type="primary", use_container_width=True):
                if name and email and password and confirm_password:
                    if password == confirm_password:
                        st.session_state.logged_in = True
                        # Generate consistent integer user_id from email
                        st.session_state.user_id = abs(hash(email)) % 1000000
                        st.session_state.user_email = email
                        st.session_state.page = 'subjects'
                        st.success("Registration successful!")
                        st.rerun()
                    else:
                        st.error("Passwords don't match")
                else:
                    st.error("Please fill in all fields")

        st.markdown("")
        # Back to landing
        if st.button('← Back to Home', use_container_width=True):
            st.session_state.page = 'landing'
            st.rerun()


def render_subjects_page():
    """Enhanced subjects page with proper grid layout"""
    render_navbar()

    # Subject data with enhanced descriptions and colors - All 9 subjects
    subjects_data = {
        "Mathematics": {
            "icon": "📐",
            "description": "Algebra, Calculus, Geometry, Statistics",
            "color": "#667eea"
        },
        "Physics": {
            "icon": "⚡",
            "description": "Mechanics, Thermodynamics, Electromagnetism",
            "color": "#ff6b6b"
        },
        "Chemistry": {
            "icon": "🧪",
            "description": "Organic, Inorganic, Physical Chemistry",
            "color": "#f093fb"
        },
        "Biology": {
            "icon": "🧬",
            "description": "Cell Biology, Genetics, Ecology",
            "color": "#fa709a"
        },
        "English Literature": {
            "icon": "📚",
            "description": "Literature, Grammar, Writing",
            "color": "#43e97b"
        },
        "History": {
            "icon": "🏛️",
            "description": "World History, Ancient Civilizations",
            "color": "#4facfe"
        },
        "Economics": {
            "icon": "💰",
            "description": "Micro, Macro, International Economics",
            "color": "#a8edea"
        },
        "Computer Science": {
            "icon": "💻",
            "description": "Programming, Algorithms, Data Structures",
            "color": "#764abc"
        },
        "Geography": {
            "icon": "🌍",
            "description": "Physical, Human, Environmental",
            "color": "#20bf6b"
        }
    }

    # Create 3 columns for grid layout (9 subjects = 3 rows of 3)
    cols = st.columns(3)

    for idx, (subject, info) in enumerate(subjects_data.items()):
        with cols[idx % 3]:
            # Create styled subject card with HTML
            card_html = f"""
            <div class="subject-card" style="
                background: linear-gradient(135deg, {info['color']} 0%, rgba(255,255,255,0.1) 100%);
                padding: 1.5rem;
                border-radius: 20px;
                text-align: center;
                margin: 0.5rem 0 1rem 0;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                border: 1px solid rgba(255,255,255,0.2);
                backdrop-filter: blur(10px);
                min-height: 200px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                position: relative;
                overflow: hidden;
            ">
                <div style="font-size: 3.5rem; margin-bottom: 0.8rem; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));">{info['icon']}</div>
                <h2 style="color: white; font-weight: bold; margin-bottom: 0.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); font-size: 1.3rem;">{subject}</h2>
                <p style="color: rgba(255,255,255,0.9); font-size: 0.85rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); line-height: 1.3; margin-bottom: 1rem;">{info['description']}</p>
                <div style="
                    position: absolute;
                    top: -50%;
                    right: -50%;
                    width: 100%;
                    height: 100%;
                    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                    pointer-events: none;
                "></div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

            # Button positioned below the card
            if st.button(f"Start Learning", key=f"select_{subject}", help=f"Start {subject} homework session", use_container_width=True, type="primary"):
                st.session_state.selected_subject = subject
                st.session_state.page = 'questions'
                st.rerun()

def render_profile_page():
    """Profile page with user stats and achievements"""
    render_navbar()

    st.markdown("# My Profile")

    # User info section
    col1, col2 = st.columns([1, 3])

    with col1:
        # Profile avatar
        st.markdown("""
        <div style="text-align: center;">
            <div style="width: 100px; height: 100px; background: linear-gradient(45deg, #FFD700, #FFA500);
                        border-radius: 50%; display: flex; align-items: center; justify-content: center;
                        margin: 0 auto; font-size: 2rem; font-weight: bold; color: white;">
                JD
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        username = st.session_state.get('username', 'John Doe')
        email = st.session_state.get('user_email', 'john.doe@example.com')
        st.markdown(f"## {username}")
        st.markdown(f"📧 {email}")
        st.markdown("🎓 Grade 10")

    st.markdown("---")

    # Stats section
    col1, col2, col3 = st.columns(3)

    # Get user stats from history
    user_id = st.session_state.get("user_id")
    total_questions = 0
    subjects_studied = 0
    day_streak = 0

    if user_id:
        try:
            rows = load_history(user_id, limit=1000)  # Get all history
            total_questions = len(rows)
            subjects_studied = len(set(row[1] for row in rows))  # Unique subjects
            day_streak = min(total_questions, 15)  # Simple streak calculation
        except:
            pass

    with col1:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.2); padding: 1.5rem; border-radius: 15px; text-align: center;">
            <div style="font-size: 2rem;">📚</div>
            <div style="font-size: 2rem; font-weight: bold; color: #FFD700;">{total_questions}</div>
            <div>Questions Asked</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.2); padding: 1.5rem; border-radius: 15px; text-align: center;">
            <div style="font-size: 2rem;">🎯</div>
            <div style="font-size: 2rem; font-weight: bold; color: #FFD700;">{subjects_studied}</div>
            <div>Subjects Studied</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.2); padding: 1.5rem; border-radius: 15px; text-align: center;">
            <div style="font-size: 2rem;">🔥</div>
            <div style="font-size: 2rem; font-weight: bold; color: #FFD700;">{day_streak}</div>
            <div>Day Streak</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Achievements section
    st.markdown("## 🏆 Achievements")
    st.markdown("Your learning milestones")

    col1, col2 = st.columns(2)

    with col1:
        # First Question achievement
        first_q_unlocked = total_questions >= 1
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, {'0.3' if first_q_unlocked else '0.1'});
                    padding: 1rem; border-radius: 10px; margin: 0.5rem 0;
                    opacity: {'1' if first_q_unlocked else '0.5'};">
            <div style="font-size: 1.5rem;">🌟 First Question</div>
            <div>Asked your first question</div>
        </div>
        """, unsafe_allow_html=True)

        # Subject Master achievement
        subject_master = subjects_studied >= 3
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, {'0.3' if subject_master else '0.1'});
                    padding: 1rem; border-radius: 10px; margin: 0.5rem 0;
                    opacity: {'1' if subject_master else '0.5'};">
            <div style="font-size: 1.5rem;">🎓 Subject Master</div>
            <div>Studied 3+ subjects in a subject</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Quick Learner achievement
        quick_learner = total_questions >= 10
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, {'0.3' if quick_learner else '0.1'});
                    padding: 1rem; border-radius: 10px; margin: 0.5rem 0;
                    opacity: {'1' if quick_learner else '0.5'};">
            <div style="font-size: 1.5rem;">⚡ Quick Learner</div>
            <div>Completed 10 questions in one day</div>
        </div>
        """, unsafe_allow_html=True)

        # Streak Champion achievement
        streak_champ = day_streak >= 7
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, {'0.3' if streak_champ else '0.1'});
                    padding: 1rem; border-radius: 10px; margin: 0.5rem 0;
                    opacity: {'1' if streak_champ else '0.5'};">
            <div style="font-size: 1.5rem;">🔥 Streak Champion</div>
            <div>Maintained a 7+ day streak</div>
        </div>
        """, unsafe_allow_html=True)

def render_about_page():
    """About Us page with company mission and info"""
    render_navbar()

    # Header with logo
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <div style="font-size: 4rem; margin-bottom: 1rem;">👑</div>
        <h1>About <span style="color: #FFD700;">EduLLM</span></h1>
        <p style="font-size: 1.2rem; color: #888; max-width: 600px; margin: 0 auto;">
            We're revolutionizing education by making high-quality, personalized learning
            assistance accessible to every student through the power of artificial intelligence.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Our Mission section
    st.markdown("## 🎯 Our Mission")

    st.markdown("""
    At EduLLM, we believe that every student deserves access to personalized, high-quality
    educational support. Our mission is to democratize learning by providing an AI-powered
    homework assistant that helps students understand complex concepts, complete assignments, and
    build confidence in their academic abilities. We're not just providing answers - we're fostering
    understanding and encouraging critical thinking.
    """)

    st.markdown("---")

    # Why Choose EduLLM section
    st.markdown("## 🌟 Why Choose EduLLM?")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🤖 AI-Powered Learning
        Our advanced AI understands your questions and provides detailed, step-by-step explanations
        that help you learn, not just get answers.

        ### 📚 Multi-Subject Support
        From Mathematics to Literature, Chemistry to History - we cover all major academic subjects
        with specialized knowledge in each area.

        ### ⚡ Instant Help
        Get help whenever you need it. Our AI tutor is available 24/7 to assist with your homework
        and study questions.
        """)

    with col2:
        st.markdown("""
        ### 🎯 Personalized Experience
        Every student learns differently. Our AI adapts to your learning style and provides
        explanations tailored to your level.

        ### 🏆 Track Your Progress
        Monitor your learning journey with detailed progress tracking, achievements, and
        personalized insights.

        ### 🔒 Safe & Secure
        Your privacy matters. We maintain the highest standards of data security and never
        share your personal information.
        """)

    st.markdown("---")

    # Our Values section
    st.markdown("## 💎 Our Values")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🎓</div>
            <h3>Excellence</h3>
            <p>We strive for the highest quality in everything we do, from our AI technology to our user experience.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🤝</div>
            <h3>Accessibility</h3>
            <p>Education should be available to everyone, regardless of background or circumstances.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🚀</div>
            <h3>Innovation</h3>
            <p>We continuously push the boundaries of what's possible in educational technology.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Contact section
    st.markdown("## 📞 Get in Touch")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### Contact Information
        📧 **Email:** support@edullm.com
        📱 **Phone:** +1 (555) 123-4567
        🌐 **Website:** www.edullm.com
        📍 **Address:** 123 Education St, Learning City, LC 12345
        """)

    with col2:
        st.markdown("""
        ### Follow Us
        🐦 **Twitter:** @EduLLM
        📘 **Facebook:** /EduLLM
        💼 **LinkedIn:** /company/edullm
        📸 **Instagram:** @edullm_official
        """)

    st.markdown("---")

    # Footer
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; color: #888;">
        <p>© 2024 EduLLM. All rights reserved. | Privacy Policy | Terms of Service</p>
        <p>Empowering students worldwide with AI-powered learning assistance.</p>
    </div>
    """, unsafe_allow_html=True)

def render_questions_page():
    """Questions page with hamburger menu"""
    render_hamburger_navbar()

    subject = st.session_state.selected_subject


    st.markdown("---")

    # Question input
    question = st.text_area(
        f"📝 Enter your {subject} question:",
        height=150,
        placeholder=f"Ask your {subject} question here...",
        help="Be specific and include all relevant details"
    )

    if st.button("🎯 Get Solution", type="primary"):
        if question.strip():
            with st.spinner("Getting solution..."):
                response = get_api_response(question, subject)

                if response:
                    st.markdown("---")
                    st.markdown(f"## 📚 {subject} Solution")

                    # Display solution (render HTML for math/formatting)
                    formatted_response = format_response(response)
                    st.markdown(f"""
                    <div class="solution-content">
                        {formatted_response}
                    </div>
                    """, unsafe_allow_html=True)

                    # Show diagram if needed
                    if should_show_diagram(question, subject):
                        st.markdown("### 📊 Visualization")
                        viz = create_smart_visualization(question, subject)
                        if viz:
                            st.image(viz, use_container_width=True)

                    # Save to history (backend first, fallback local)
                    if backend_save_history(subject, question.strip(), formatted_response):
                        pass  # Successfully saved
                    else:
                        # Fallback to local save if backend fails
                        user_id = st.session_state.get("user_id")
                        if user_id:
                            save_history(user_id, subject, question.strip(), formatted_response)

                    # Feedback
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

    # Subject-specific History
    with st.expander(f"🕘 View your {subject} history"):
        # Try to load subject-specific history from backend first, fallback to local
        rows = backend_get_history(limit=25, subject=subject)
        if not rows:
            user_id = st.session_state.get("user_id")
            if user_id:
                rows = load_history(user_id, limit=25, subject=subject)
        if not rows:
            st.info(f"No {subject} history yet.")
        else:
            for row in rows:
                # Handle both backend format (dict) and local format (tuple)
                if isinstance(row, dict):
                    subj = row.get('subject', 'Unknown')
                    q = row.get('question', 'No question')
                    created_at = row.get('created_at', 'Unknown time')
                else:
                    # Local format: (id, subject, question, answer, created_at)
                    _id, subj, q, a, created_at = row
                st.markdown(f"**[{created_at}] {subj}**")
                st.markdown(f"- Question: {q}")
                st.markdown("---")

    # All subjects history
    with st.expander("📚 View all subjects history"):
        # Try to load all history from backend first, fallback to local
        rows = backend_get_history(limit=50)
        if not rows:
            user_id = st.session_state.get("user_id")
            if user_id:
                rows = load_history(user_id, limit=50)
        if not rows:
            st.info("No history yet.")
        else:
            for row in rows:
                # Handle both backend format (dict) and local format (tuple)
                if isinstance(row, dict):
                    subj = row.get('subject', 'Unknown')
                    q = row.get('question', 'No question')
                    created_at = row.get('created_at', 'Unknown time')
                else:
                    # Local format: (id, subject, question, answer, created_at)
                    _id, subj, q, a, created_at = row
                st.markdown(f"**[{created_at}] {subj}**")
                st.markdown(f"- Question: {q}")
                st.markdown("---")

def main():
    """Main application with complete workflow"""
    # Initialize database
    init_db()

    # Load CSS
    load_css()

    # Route to appropriate page
    if st.session_state.page == 'landing':
        render_landing_page()
    elif st.session_state.page == 'login':
        render_login_page()
    elif st.session_state.page == 'subjects':
        if st.session_state.logged_in:
            render_subjects_page()
        else:
            st.session_state.page = 'login'
            st.rerun()
    elif st.session_state.page == 'questions':
        if st.session_state.logged_in and st.session_state.selected_subject:
            render_questions_page()
        else:
            st.session_state.page = 'subjects'
            st.rerun()
    elif st.session_state.page == 'profile':
        if st.session_state.logged_in:
            render_profile_page()
        else:
            st.session_state.page = 'login'
            st.rerun()
    elif st.session_state.page == 'about':
        render_about_page()

if __name__ == "__main__":
    main()