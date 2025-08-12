import streamlit as st
import requests
import json
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import re
import html

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
    /* Code block styling for Computer Science output */
    .code-block {
        background-color: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 8px;
        padding: 1.25rem 1.25rem;
        margin: 1rem 0;
        overflow-x: auto;
    }
    .code-block pre, .code-block code {
        font-family: 'Courier New', monospace;
        color: #e0e0e0;
        font-size: 1.05em;
        line-height: 1.5;
        white-space: pre;
    }
    .code-header {
        font-size: 0.85em;
        color: #bbb;
        margin-bottom: 0.25rem;
    }
    /* One-line step header with next-line code-like explanation */
    .step-code {
        background-color: rgba(255,255,255,0.04);
        border: 1px dashed rgba(76,175,80,0.6);
        border-radius: 6px;
        padding: 0.6rem 0.8rem;
        margin: 0.4rem 0 0.8rem 0;
        font-family: 'Courier New', monospace;
        color: #d8f0dc;
        font-size: 0.98em;
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
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('white')

        if subject == "Mathematics":
            # Lightweight geometry engine (shapes + graphs)
            if any(k in question_lower for k in [
                'triangle', 'abc', 'perpendicular bisector', 'bisector', 'median', 'altitude',
                'angle bisector', 'parallel', 'perpendicular', 'circle', 'circumcircle', 'incenter', 'circumcenter',
                'square', 'rectangle', 'polygon', 'semicircle', 'pentagon', 'hexagon', 'heptagon', 'octagon'
            ]):
                # ---------- Helpers ----------
                def find_len(name: str):
                    pattern = rf"{name}\s*=?\s*(\d+(?:\.\d+)?)\s*cm"
                    m = re.search(pattern, question, flags=re.IGNORECASE)
                    return float(m.group(1)) if m else None

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

                # ---------- Build baseline triangle if ABC mentioned or side lengths provided ----------
                ab = find_len('AB')
                bc = find_len('BC')
                ac = find_len('AC')

                need_triangle = any(k in question_lower for k in ['triangle', ' abc', 'abc ', '△abc', '△ abc']) or any(v is not None for v in [ab, bc, ac])

                points = {}
                if need_triangle:
                    if bc is None and ab is None and ac is None:
                        ab, bc, ac = 5.0, 6.0, 4.0
                    else:
                        bc = 6.0 if bc is None else bc
                        ab = 5.0 if ab is None else ab
                        ac = 4.0 if ac is None else ac

                    B = (0.0, 0.0)
                    C = (bc, 0.0)
                    # circle-circle intersection to get A (choose upper solution)
                    x_a = (ab**2 - ac**2 + bc**2) / (2 * bc if bc != 0 else 1e-6)
                    y_sq = max(ab**2 - x_a**2, 0.0)
                    y_a = float(np.sqrt(y_sq))
                    A = (x_a, y_a)
                    points.update({'A': A, 'B': B, 'C': C})

                    # Draw triangle with black outlines for white background
                    stroke = '#000000'
                    draw_line(B, C, color=stroke, linewidth=2)
                    draw_line(C, A, color=stroke, linewidth=2)
                    draw_line(A, B, color=stroke, linewidth=2)
                    ax.scatter([A[0], B[0], C[0]], [A[1], B[1], C[1]], color='#000000', zorder=3)
                    ax.text(B[0], B[1] - 0.2, 'B', ha='center', va='top', color=stroke)
                    ax.text(C[0], C[1] - 0.2, 'C', ha='center', va='top', color=stroke)
                    ax.text(A[0], A[1] + 0.2, 'A', ha='center', va='bottom', color=stroke)

                    # Side length labels
                    def put_len(p, q, label):
                        mx, my = (p[0]+q[0])/2.0, (p[1]+q[1])/2.0
                        ax.text(mx, my + 0.15, label, color=stroke, ha='center', va='bottom')
                    put_len(B, C, f'{bc} cm')
                    put_len(A, B, f'{ab} cm')
                    put_len(A, C, f'{ac} cm')

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

                # Simple Circle Generation (like triangle approach)
                circle_match = re.search(r'circle.*?radius\s*(\d+(?:\.\d+)?)|radius\s*(\d+(?:\.\d+)?)', question, flags=re.IGNORECASE)
                if circle_match or 'circle' in question_lower:
                    # Extract radius simply
                    radius = 4.0  # good default size
                    if circle_match:
                        radius = float(circle_match.group(1) or circle_match.group(2))
                    
                    # Simple circle at origin
                    stroke = '#000000'
                    circle = plt.Circle((0, 0), radius, fill=False, edgecolor=stroke, linewidth=2)
                    ax.add_patch(circle)
                    
                    # Center point
                    ax.scatter([0], [0], color=stroke, s=30, zorder=3)
                    ax.text(0, 0.3, 'O', ha='center', va='bottom', color=stroke, fontweight='bold')
                    
                    # Radius line
                    ax.plot([0, radius], [0, 0], color=stroke, linestyle='--', linewidth=1.5)
                    ax.text(radius/2, 0.2, f'r = {radius}', ha='center', va='bottom', color=stroke)
                    
                    # Simple bounds like triangle
                    ax.set_xlim(-radius-1, radius+1)
                    ax.set_ylim(-radius-1, radius+1)
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

                # Regular shapes when requested without triangle context
                if not points and any(k in question_lower for k in ['square', 'rectangle', 'polygon', 'circle', 'semicircle']):
                    stroke = '#000000'
                    if 'square' in question_lower:
                        s = 4.0
                        X = np.array([0, s, s, 0, 0]); Y = np.array([0, 0, s, s, 0])
                        ax.plot(X, Y, color=stroke, linewidth=2)
                        # mark vertices and lengths
                        V = [(0,0), (s,0), (s,s), (0,s)]
                        labels = ['A','B','C','D']
                        ax.scatter([p[0] for p in V], [p[1] for p in V], color=stroke)
                        for (px,py),lab in zip(V,labels):
                            ax.text(px, py-0.2 if py==0 else py+0.2, lab, color=stroke, ha='center', va='center')
                        ax.text(s/2, -0.3, f'{s} cm', color=stroke, ha='center')
                        ax.text(s+0.3, s/2, f'{s} cm', color=stroke, va='center')
                        ax.set_title('Square')
                    elif 'rectangle' in question_lower:
                        a, b = 6.0, 4.0
                        X = np.array([0, a, a, 0, 0]); Y = np.array([0, 0, b, b, 0])
                        ax.plot(X, Y, color=stroke, linewidth=2)
                        V = [(0,0), (a,0), (a,b), (0,b)]
                        labels = ['A','B','C','D']
                        ax.scatter([p[0] for p in V], [p[1] for p in V], color=stroke)
                        for (px,py),lab in zip(V,labels):
                            ax.text(px, py-0.2 if py==0 else py+0.2, lab, color=stroke, ha='center', va='center')
                        ax.text(a/2, -0.3, f'{a} cm', color=stroke, ha='center')
                        ax.text(a+0.3, b/2, f'{b} cm', color=stroke, va='center')
                        ax.set_title('Rectangle')
                    elif 'semicircle' in question_lower:
                        r = 3.0
                        t = np.linspace(0, np.pi, 200)
                        ax.plot(r*np.cos(t), r*np.sin(t), color=stroke, linewidth=2)
                        ax.plot([-r, r], [0, 0], color=stroke, linewidth=2)
                        # points and labels
                        A = (-r,0); B = (r,0); O = (0,0)
                        ax.scatter([A[0],B[0],O[0]],[A[1],B[1],O[1]], color=stroke)
                        ax.text(A[0], A[1]-0.2, 'A', color=stroke, ha='center')
                        ax.text(B[0], B[1]-0.2, 'B', color=stroke, ha='center')
                        ax.text(O[0], O[1]+0.2, 'O', color=stroke, ha='center')
                        ax.text(0, -0.3, f'{2*r} cm', color=stroke, ha='center')
                        ax.set_aspect('equal')
                        ax.set_title('Semicircle')
                    elif 'circle' in question_lower:
                        # Simple circle like triangle approach
                        r = 4.0  # default radius
                        radius_match = re.search(r'radius\s*(\d+(?:\.\d+)?)', question_lower)
                        if radius_match:
                            r = float(radius_match.group(1))
                        
                        # Simple circle
                        circle = plt.Circle((0, 0), r, fill=False, edgecolor=stroke, linewidth=2)
                        ax.add_patch(circle)
                        ax.scatter([0], [0], color=stroke, s=30, zorder=3)
                        ax.text(0, 0.3, 'O', ha='center', va='bottom', color=stroke, fontweight='bold')
                        ax.plot([0, r], [0, 0], color=stroke, linestyle='--', linewidth=1.5)
                        ax.text(r/2, 0.2, f'r = {r}', ha='center', va='bottom', color=stroke)
                        ax.set_xlim(-r-1, r+1)
                        ax.set_ylim(-r-1, r+1)
                        ax.set_aspect('equal')
                    elif 'polygon' in question_lower:
                        # default to regular hexagon
                        n = 6
                        t = np.linspace(0, 2*np.pi, n+1)
                        X = np.cos(t); Y = np.sin(t)
                        ax.plot(X, Y, color=stroke, linewidth=2)
                        # label vertices
                        verts = list(zip(X[:-1], Y[:-1]))
                        labels = ['A','B','C','D','E','F','G','H']
                        for i,(px,py) in enumerate(verts):
                            ax.scatter([px],[py], color=stroke)
                            ax.text(px, py+0.15, labels[i], color=stroke, ha='center')
                        ax.set_aspect('equal')
                        ax.set_title('Regular Polygon (hexagon)')

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
                    # Patches
                    for patch in ax.patches:
                        try:
                            verts = patch.get_path().transformed(patch.get_transform()).vertices
                            if verts is not None and len(verts) > 0:
                                x_all.extend(list(verts[:,0])); y_all.extend(list(verts[:,1]))
                        except Exception:
                            pass
                    # Collections
                    for coll in ax.collections:
                        try:
                            offs = coll.get_offsets()
                            if offs is not None and len(offs) > 0:
                                arr = np.array(offs)
                                if arr.ndim == 2 and arr.shape[1] == 2:
                                    x_all.extend(list(arr[:,0])); y_all.extend(list(arr[:,1]))
                        except Exception:
                            pass
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
        plt.savefig(buf, format='png', dpi=180, facecolor='white')
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
    
    # Choose model (Physics gets a stronger one) and prepare request body
    primary_model = "openai/gpt-4o-mini"
    if subject in ("Physics", "Chemistry"):
        primary_model = "openai/gpt-4o"

    fallback_model = "openai/gpt-4o-mini"  # previously working model

    def _make_body(model_name: str):
        return {
            "model": model_name,
            "messages": [
                {"role": "system", "content": SUBJECTS[subject]['prompt']},
                {"role": "user", "content": question}
            ],
            "temperature": 0.1,
            "max_tokens": 2000
        }
    
    try:
        # First try with the primary model
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=_make_body(primary_model),
            timeout=30
        )

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']

        # If primary fails, silently try a safe fallback (no noisy UI messages)

        response_fb = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=_make_body(fallback_model),
            timeout=30
        )

        if response_fb.status_code == 200:
            return response_fb.json()['choices'][0]['message']['content']

        # If fallback also fails, show a minimal, user-friendly message only
        st.error("The service is temporarily unavailable. Please try again in a moment.")
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
        
        # Example section removed per user request
    
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
                        
                        # Improved formatting in a clean container
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
