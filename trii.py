# app.py
import streamlit as st
import requests
import matplotlib.pyplot as plt
import numpy as np
import json
from io import BytesIO
import PIL.Image
import math
import re

# === API Setup ===
API_URL = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": "Bearer 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",
    "Content-Type": "application/json"
}

# === Helpers & Config ===
CM_TO_INCH = 0.3937007874
FIG_CM = 6            # desired figure side in cm
FIG_INCH = FIG_CM * CM_TO_INCH

st.set_page_config(layout="wide", page_title="LLM Math Solver")

# === LLM Call (for textual solution) ===
def query_llm_solution(prompt):
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "temperature": 0.0,
        "messages": [
            {"role": "system", "content": (
                "You are a math tutor generating textbook-style, step-by-step solutions.\n"
                "Format everything like a clean math document:\n"
                "- Use bold headings like **Step 1**, **Final Answer**.\n"
                "- Start each heading on a new line, leave one blank line.\n"
                "- Put explanation on the next line.\n"
                "- Display equations centered using $$...$$.\n"
                "- Do NOT use \\frac or \\cdot. Use plain fractions like 1/2.\n"
            )},
            {"role": "user", "content": prompt}
        ]
    }
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    if resp.status_code == 200:
        try:
            return resp.json()['choices'][0]['message']['content']
        except Exception:
            return f"Error: Unexpected LLM response structure."
    else:
        return f"Error: {resp.status_code} - {resp.text}"

# === LLM Call (for triangle JSON extraction) ===
def extract_triangle_json(question):
    prompt = f"""
You are an assistant that extracts triangle construction parameters from a geometry question.

Task:
1. Identify the triangle's three points (vertices), return like ["A","B","C"] (use order as they appear).
2. Extract given side lengths as a dictionary like {{"AB": 5}} (numbers only, units cm).
3. Extract given angles as a dictionary like {{"ABC": 60}} (degrees).
4. Detect the triangle type (SSS, SAS, ASA, SSA, AAS) based on what's given.

Ignore extras like "mark vertices", "use compass", etc.
Return only a JSON object exactly (no explanation). Example:
{{
  "points": ["A","B","C"],
  "sides": {{"AB": 5, "BC": 6}},
  "angles": {{"ABC": 60}},
  "triangle_type": "SAS"
}}
Now process this question:
{question}
"""
    payload = {
        "model": "openai/gpt-3.5-turbo",
        "temperature": 0,
        "messages": [
            {"role": "system", "content": "Extract triangle data in JSON only. No text explanation."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        resp = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    except Exception as e:
        print("LLM request error:", e)
        return None

    if resp.status_code == 200:
        content = resp.json().get('choices', [{}])[0].get('message', {}).get('content', '')
        try:
            return json.loads(content)
        except Exception as e:
            print("JSON parse fail:", e, "raw:", content)
            return None
    else:
        print("LLM non-200:", resp.status_code, resp.text)
        return None

# === Input cleaning: remove known filler phrases, keep numeric data and specs ===
def clean_input_text(q):
    q = q.strip()
    # remove common filler phrases the user often types
    fillers = [
        "use a compass and protractor", "use a compass", "and mark all vertices clearly",
        "mark all vertices clearly", "mark all vertices", "mark all vertices clearly.", "mark all vertices.",
        "show work", "show steps", "sketch", "draw", "construct"
    ]
    for f in fillers:
        q = q.replace(f, "")
    # normalize degree symbols to '°'
    q = q.replace(" degrees", "°").replace(" degree", "°")
    # compress spaces and return first sentence if user pastes many instructions but keep entire text if needed
    q = re.sub(r'\s+', ' ', q).strip()
    return q

# === Geometry math helpers ===
def law_of_cosine_angle(a, b, c):
    # returns angle opposite side a, given sides a,b,c
    # cos(A) = (b^2 + c^2 - a^2) / (2 b c)
    denom = 2 * b * c
    val = (b*b + c*c - a*a) / denom if denom != 0 else 1
    val = min(1, max(-1, val))
    return math.degrees(math.acos(val))

def law_of_cosine_side(b, c, A_deg):
    A = math.radians(A_deg)
    a = math.sqrt(b*b + c*c - 2*b*c*math.cos(A))
    return a

def law_of_sines_side(a, A_deg, B_deg):
    # returns b: b/sin(B) = a/sin(A)
    return a * math.sin(math.radians(B_deg)) / math.sin(math.radians(A_deg))

# === Drawing strategies ===
def draw_SSS(sides, points):
    # sides dict has three sides e.g. AB, BC, AC
    A, B, C = points
    # prefer AB, BC, AC
    AB = sides.get(f"{A}{B}") or sides.get(f"{B}{A}")
    BC = sides.get(f"{B}{C}") or sides.get(f"{C}{B}")
    AC = sides.get(f"{A}{C}") or sides.get(f"{C}{A}")
    if not all([AB, BC, AC]): 
        return None
    # Place AB on x-axis
    P1 = (0.0, 0.0)
    P2 = (AB, 0.0)
    # compute C using known sides AC and BC: intersection of two circles
    # circle centered at P1 radius AC; circle centered at P2 radius BC
    # using standard circle intersection formula
    d = AB
    # handle impossible geometry
    if d == 0:
        return None
    # check intersection
    if (AC + BC < d) or (abs(AC - BC) > d):
        return None
    # distance from P1 along line to midpoint between intersections
    a = (AC*AC - BC*BC + d*d) / (2*d)
    h = math.sqrt(max(0.0, AC*AC - a*a))
    xm = a / d * (P2[0] - P1[0]) + P1[0]
    ym = a / d * (P2[1] - P1[1]) + P1[1]
    # choose positive h (upper)
    rx = - (P2[1] - P1[1]) * (h / d)
    ry = (P2[0] - P1[0]) * (h / d)
    P3 = (xm + rx, ym + ry)
    return P1, P2, P3

def draw_SAS(sides, angles, points):
    A, B, C = points
    # SAS: two sides and included angle (we'll try AB and BC with angle ABC)
    AB = sides.get(f"{A}{B}") or sides.get(f"{B}{A}")
    BC = sides.get(f"{B}{C}") or sides.get(f"{C}{B}")
    # find an angle that has B in middle (i.e., ABC)
    angle_val = None
    for k, v in angles.items():
        # look for pattern like ABC where B is middle char
        if len(k) >= 3 and k[1] == B:
            angle_val = v
            break
    if not (AB and BC and angle_val):
        return None
    # Place AB on x-axis (P1 at A, P2 at B)
    P1 = (0.0, 0.0)
    P2 = (AB, 0.0)
    # compute C from B with length BC and angle measured at B from BA to BC.
    # angle ABC means angle with vertex B between BA and BC. BA vector points from B to A = (-AB,0)
    # We assume angle measured from positive x (BA direction) CCW — for drawing we simply place BC at angle (180 - angle) from x-axis
    # Simpler: compute P3 relative to P2: angle measured from positive x-axis equals 180° - angle_val
    theta = math.radians(180 - angle_val)
    Px = P2[0] + BC * math.cos(theta)
    Py = P2[1] + BC * math.sin(theta)
    P3 = (Px, Py)
    return P1, P2, P3

def draw_ASA_AAS(sides, angles, points):
    # If we have an ASA or AAS: we have two angles and one side.
    A, B, C = points
    # get side we have
    side_key = next(iter(sides.keys()))
    side_length = sides[side_key]
    # side_key like AB: end points
    p1, p2 = side_key[0], side_key[1]
    # identify which angle is included or not
    # Strategy: pick the given side as base, compute other vertices using angles and law of sines.
    # Get two angles:
    angle_items = list(angles.items())
    if len(angle_items) < 2:
        return None
    # We'll try to map angles to vertex labels straightforwardly (angles keys like ABC)
    # Extract degree for each vertex (middle character)
    angle_at = {k[1]: v for k, v in angles.items() if len(k) >= 3}
    # if side is AB, then place A at origin, B at (side_length,0); need angles at A and B (or one of them + third)
    if p1 in angle_at and p2 in angle_at:
        A_label = p1
        B_label = p2
        angleA = angle_at[p1]
        angleB = angle_at[p2]
        angleC = 180 - (angleA + angleB)
        # apply law of sines to compute other sides:
        # side opposite angleC is AB? depends — careful mapping: side AB is between A and B so opposite is angle C.
        # Given AB = side_length, opposite angle is angleC.
        # Using law of sines: AC / sin(B) = AB / sin(C)
        if angleC <= 0: return None
        AC = side_length * math.sin(math.radians(angleB)) / math.sin(math.radians(angleC))
        BC = side_length * math.sin(math.radians(angleA)) / math.sin(math.radians(angleC))
        # now we can place:
        P1 = (0.0, 0.0)        # A
        P2 = (side_length, 0)  # B
        # compute C coordinates by intersection of circles (same as SSS with AC and BC)
        d = side_length
        a = (AC*AC - BC*BC + d*d) / (2*d)
        h = math.sqrt(max(0.0, AC*AC - a*a))
        xm = a / d * (P2[0] - P1[0]) + P1[0]
        ym = a / d * (P2[1] - P1[1]) + P1[1]
        rx = - (P2[1] - P1[1]) * (h / d)
        ry = (P2[0] - P1[0]) * (h / d)
        P3 = (xm + rx, ym + ry)
        # map points to provided order A,B,C — we may need to permute to match
        mapping = {p1: P1, p2: P2}
        # find the remaining label
        remaining_label = next(lbl for lbl in points if lbl not in (p1, p2))
        mapping[remaining_label] = P3
        # return in order points
        return mapping[points[0]], mapping[points[1]], mapping[points[2]]
    else:
        # fallback: try another mapping (not exhaustive)
        return None

def draw_SSA(sides, angles, points):
    # Ambiguous case: two sides and an angle not included -> may have 0,1,2 solutions
    A, B, C = points
    # find given sides and angle:
    # suppose sides AB and BC known and angle at A known => different cases; this function attempts one practical placement
    # We'll attempt to find a configuration using law of sines
    # get two side names:
    side_items = list(sides.items())
    if len(side_items) < 2:
        return None
    # attempt a common case: given AB (base), AC (side) and angle at A -> compute possible C
    # Find a side that includes A
    sideA = None
    for k, v in sides.items():
        if k[0] == A or k[1] == A:
            sideA = (k, v)
            break
    if not sideA:
        return None
    kA, valA = sideA
    # identify angle at A:
    angle_items = {k: v for k, v in angles.items()}
    angleA = None
    for k, v in angle_items.items():
        if len(k) >= 3 and k[1] == A:
            angleA = v
            break
    # find the other side that's not the AB base maybe
    other_side = None
    for k, v in sides.items():
        if k != kA:
            other_side = (k, v)
            break
    if not (angleA and other_side):
        return None
    # we'll do a straightforward constructive attempt: place base sideA on x-axis with endpoints P1,P2; then compute the point using law of sines
    # For brevity and to keep code deterministic, attempt numeric construction treating sideA as base and other_side as given length from A
    # Place sideA endpoints:
    # determine mapping such that sideA is AB or similar
    base_label1, base_label2 = kA[0], kA[1]
    base_length = valA
    P1 = (0.0, 0.0)     # base_label1
    P2 = (base_length, 0.0)  # base_label2
    # suppose angle at base_label1 (A) is angleA and other side from A has length s
    s = other_side[1]
    # two possible positions for the point at distance s from A: compute circle intersection with circle centered at A radius s and with B to satisfy? This quickly becomes many permutations.
    # For practicality: place third vertex at angle angleA from the base (choose one), and distance s from A
    theta = math.radians(angleA)
    P3 = (P1[0] + s * math.cos(theta), P1[1] + s * math.sin(theta))
    return P1, P2, P3

# === Unified draw_triangle orchestrator ===
def draw_triangle(points, sides, angles, detected_type=None):
    # sides and angles are dict with numeric values
    # points is list of three labels in order
    try:
        # Prefer the triangle_type extracted by the LLM if available
        ttype = detected_type
        if not ttype:
            # local inference
            if len(sides) == 3:
                ttype = "SSS"
            elif len(sides) == 2 and len(angles) == 1:
                # try to recognize included angle
                # if angle key's middle vertex matches a vertex that connects both given sides -> SAS
                only_angle_key = next(iter(angles.keys())) if angles else None
                if only_angle_key:
                    mid = only_angle_key[1] if len(only_angle_key) >= 3 else None
                    # check if both sides share the mid vertex
                    side_keys = list(sides.keys())
                    shared = any(mid in k for k in side_keys)
                    if shared:
                        ttype = "SAS"
                    else:
                        ttype = "SSA"
                else:
                    ttype = "SSA"
            elif len(angles) == 2 and len(sides) == 1:
                # ASA or AAS: if side is between the two angles -> ASA else AAS
                side_key = next(iter(sides.keys()))
                mid = side_key[1]
                # if there is an angle whose middle is the midpoint, it's ASA
                if any(mid == k[1] for k in angles.keys()):
                    ttype = "ASA"
                else:
                    ttype = "AAS"
            else:
                ttype = None

        # choose drawing method
        if ttype == "SSS":
            res = draw_SSS(sides, points)
        elif ttype == "SAS":
            res = draw_SAS(sides, angles, points)
        elif ttype in ("ASA", "AAS"):
            res = draw_ASA_AAS(sides, angles, points)
        elif ttype == "SSA":
            res = draw_SSA(sides, angles, points)
        else:
            # fallback attempt using SAS placement if possible
            res = draw_SAS(sides, angles, points)

        if not res:
            return None

        # res is P1,P2,P3 coordinates
        P1, P2, P3 = res
        # generate figure sized in cm -> inches
        # ===== UPDATED: scale up the figure size slightly (no other logic changed) =====
        # keep FIG_INCH variable intact; scale it locally to increase rendered diagram size
        local_fig_inch = FIG_INCH * 1.4  # ~40% larger for clearer images
        fig, ax = plt.subplots(figsize=(local_fig_inch, local_fig_inch), dpi=150)
        # =================================================================================
        coords = np.array([P1, P2, P3, P1])
        ax.plot(coords[:, 0], coords[:, 1], 'b-', linewidth=2)
        # label vertices with their provided labels in the given order
        ax.text(P1[0], P1[1], points[0], fontsize=10, ha='right', va='top')
        ax.text(P2[0], P2[1], points[1], fontsize=10, ha='left', va='top')
        ax.text(P3[0], P3[1], points[2], fontsize=10, ha='center', va='bottom')
        # annotate lengths (midpoints)
        def mid_text(a, b, text):
            mx, my = ( (a[0]+b[0])/2, (a[1]+b[1])/2 )
            ax.text(mx, my, text, fontsize=8, ha='center', va='center', backgroundcolor='white')

        # compute side lengths
        AB_len = round(math.dist(P1, P2), 2)
        BC_len = round(math.dist(P2, P3), 2)
        CA_len = round(math.dist(P3, P1), 2)
        mid_text(P1, P2, f"{AB_len} cm")
        mid_text(P2, P3, f"{BC_len} cm")
        mid_text(P3, P1, f"{CA_len} cm")

        # if an angle was provided for vertex in middle, draw arc for it (we draw for first angle we find)
        if angles:
            for k, v in angles.items():
                if len(k) >= 3:
                    mid = k[1]
                    if mid == points[1]:  # angle at middle vertex B
                        # draw small arc at P2 with arc radius relative to figure
                        angle_val = v
                        # draw arc from 0 to angle (approx)
                        arc_r = 0.5
                        angle_rad = math.radians(angle_val)
                        arc = np.linspace(0, angle_rad, 50)
                        arc_x = P2[0] + arc_r * np.cos(arc)
                        arc_y = P2[1] + arc_r * np.sin(arc)
                        ax.plot(arc_x, arc_y, color='red')
                        ax.text(P2[0] + arc_r*math.cos(angle_rad/2), P2[1] + arc_r*math.sin(angle_rad/2), f"{angle_val}°", color='red', fontsize=8)
                        break

        ax.set_aspect('equal')
        ax.axis('off')
        return fig
    except Exception as e:
        print("draw_triangle error:", e)
        return None

# === UI Layout & Session ===
st.title("📘 Ask a Math Question (Formatted Solver)")

if "submitted" not in st.session_state:
    st.session_state["submitted"] = False
if "question" not in st.session_state:
    st.session_state["question"] = ""
if "answer" not in st.session_state:
    st.session_state["answer"] = ""
if "triangle_data" not in st.session_state:
    st.session_state["triangle_data"] = None
if "detected_type" not in st.session_state:
    st.session_state["detected_type"] = None

math_type = st.selectbox("Choose the math subject:", [
    "Algebra", "Geometry", "Calculus", "Trigonometry",
    "Arithmetic", "Probability", "Statistics", "Linear Algebra", "Other"], index=1)

question = st.text_area("Enter your math question", value=st.session_state["question"], height=180, key="qbox")
solve = st.button("🚀 Solve Question")

def minimalize_question_for_extraction(q):
    # remove extra instructions and keep only the core sentences (punctuation-aware)
    q = clean_input_text(q)
    # sometimes users paste long paragraphs; return entire cleaned q to LLM extractor (we rely on LLM JSON)
    return q

# === Stress test inputs (exam-style) ===
stress_tests = [
    "Draw a triangle PQR in which PQ = 4 cm, QR = 5 cm, and ∠PQR = 90°. Mark all vertices clearly.",
    "Construct a circle with center O and radius 6 cm. Mark points A and B such that ∠AOB = 120°.",
    "Draw a rectangle ABCD such that AB = 8 cm and BC = 6 cm. Mark all vertices.",
    "Draw an equilateral triangle XYZ with each side 7 cm. Label all sides and angles.",
    "Construct a regular pentagon inside a circle of radius 5 cm. Indicate all vertices.",
    # Extreme / tricky punctuation cases:
    "In triangle ABC: AB=13cm, BC=14 cm, CA=15 cm; find & draw altitudes, label A,B,C.",
    "Make a right triangle RST with base = 8 cm, height = 15 cm; highlight hypotenuse.",
    "Draw triangle LMN where ∠LMN = 45° and LN = 10 cm and MN = 7 cm. Mark vertices.",
    "Draw circle centre O, diameter = 25 cm; mark midpoint and draw chord AB with length 10 cm.",
    "Create a regular hexagon (6 equal sides) inscribed in a circle of radius 12 cm."
]

# Show Stress tests expander so you can load any test into the question box quickly
with st.expander("Stress tests (click Load to copy into question box)"):
    for i, t in enumerate(stress_tests):
        cols = st.columns([8,1])
        cols[0].write(f"{i+1}. {t}")
        if cols[1].button("Load", key=f"load_test_{i}"):
            st.session_state["question"] = t
            # after setting, rerun so the text area updates immediately
            st.experimental_rerun()

if solve and question.strip():
    st.session_state["submitted"] = True
    st.session_state["question"] = question
    st.session_state["answer"] = ""
    st.session_state["triangle_data"] = None
    st.session_state["detected_type"] = None

    with st.spinner("🧠 Generating solution..."):
        full_prompt = f"""
You are a professional math tutor.
This is a **{math_type}** problem.
Solve the following math question using a textbook-style structure.

---
**Formatting Instructions:**
1. Use bold headings like **Given**, **To Find**, **Step 1**, etc.
2. Put the heading on one line.
3. Leave a blank line after each heading.
4. On the next line, give a clear explanation.
5. Then put math equations centered using $$...$$
6. Do NOT use \\frac or \\cdot. Use plain math.
7. End with **Final Answer**
---

**Question:**
{question}
"""
        st.session_state["answer"] = query_llm_solution(full_prompt)

    # Attempt to extract triangle info if geometry and contains draw/construct/sketch keywords
    # ===== UPDATED: broadened detection to any a-z + geometry terms =====
    geometry_keywords = ["triangle", "circle", "square", "rectangle", "polygon",
                         "hypotenuse", "radius", "diameter", "side", "angle", "draw", "construct", "sketch",
                         "vertices", "vertex", "equilateral", "isosceles", "right-angled", "right"]
    if math_type.lower() == "geometry" and re.search(r"[a-z]", question.lower()) and any(k in question.lower() for k in geometry_keywords):
        cleaned = minimalize_question_for_extraction(question)
        data = extract_triangle_json(cleaned)
        if data and isinstance(data, dict):
            st.session_state["triangle_data"] = data
            st.session_state["detected_type"] = data.get("triangle_type")
        else:
            st.session_state["triangle_data"] = None
            st.session_state["detected_type"] = None

# === Show answer and optional sketch button ===
if st.session_state["submitted"]:
    st.markdown("---")
    st.subheader("📘 Answer:")
    # keep exact formatting output produced by the LLM
    st.markdown(st.session_state["answer"].replace("\n", "<br/>"), unsafe_allow_html=True)

    # Sketch UI (renamed to be generic diagram generation)
    if st.session_state["triangle_data"]:
        data = st.session_state["triangle_data"]
        pts = data.get("points", [])
        sides = data.get("sides", {})
        angles = data.get("angles", {})
        st.success(f"🧠 Detected Triangle Type: **{data.get('triangle_type','unknown')}**")
        st.markdown("### 📐 Diagram Construction")
        if st.button("Generate Diagram"):
            fig = draw_triangle(pts, sides, angles, detected_type=data.get("triangle_type"))
            if fig:
                buf = BytesIO()
                fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
                buf.seek(0)
                img = PIL.Image.open(buf)
                # center image in middle column with larger display width to make it easier to see
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    # increased display width for clearer view (was small previously)
                    st.image(img, caption="Generated Diagram", width=int(FIG_CM * 60))
                st.success("✅ Diagram created successfully.")
            else:
                st.warning("⚠️ Could not construct diagram — invalid combination or ambiguous data.")
    else:
        # also update info-check to the broader detection (so message shows only when appropriate)
        geometry_keywords = ["triangle", "circle", "square", "rectangle", "polygon",
                             "hypotenuse", "radius", "diameter", "side", "angle", "draw", "construct", "sketch",
                             "vertices", "vertex", "equilateral", "isosceles", "right-angled", "right"]
        if math_type.lower() == "geometry" and re.search(r"[a-z]", question.lower()) and any(k in question.lower() for k in geometry_keywords):
            st.info("ℹ️ Please include at least two sides and one angle (or 3 sides) clearly. Example: 'Draw triangle ABC with AB = 5 cm, BC = 6 cm and ∠ABC = 60°.'")

# EOF
