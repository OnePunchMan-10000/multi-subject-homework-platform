import streamlit as st
import requests
import re
import json
import math
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import PIL.Image

# === API & Config ===
API_URL = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": "Bearer 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",
    "Content-Type": "application/json"
}

CM_TO_INCH = 0.3937007874
FIG_CM = 6
FIG_INCH = FIG_CM * CM_TO_INCH

st.set_page_config(layout="wide", page_title="LLM Math Solver")

# === Geometry keywords for detection ===
GEOMETRY_KEYWORDS = [
    "triangle", "circle", "square", "rectangle", "polygon",
    "hypotenuse", "radius", "diameter", "side", "angle", "draw",
    "construct", "sketch", "vertices", "vertex", "equilateral",
    "isosceles", "right-angled", "right"
]

# === LLM Call for solution ===
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
            return "Error: Unexpected LLM response structure."
    else:
        return f"Error: {resp.status_code} - {resp.text}"

# === LLM Call for triangle JSON extraction ===
def extract_triangle_json(question):
    prompt = f"""
You are an assistant that extracts triangle construction parameters from a geometry question.

Task:
1. Identify the triangle's three points (vertices), return like ["A","B","C"] (in order).
2. Extract side lengths as a dictionary like {{"AB": 5}} (numbers only, cm).
3. Extract angles as a dictionary like {{"ABC": 60}} (degrees).
4. Detect triangle type (SSS, SAS, ASA, SSA, AAS).

Ignore extras like "mark vertices", etc.
Return ONLY a JSON object exactly (no explanation). Example:
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

# === Input cleaning ===
def clean_input_text(q):
    q = q.strip()
    fillers = [
        "use a compass and protractor", "use a compass", "and mark all vertices clearly",
        "mark all vertices clearly", "mark all vertices", "mark all vertices clearly.", "mark all vertices.",
        "show work", "show steps", "sketch", "draw", "construct"
    ]
    for f in fillers:
        q = q.replace(f, "")
    q = q.replace(" degrees", "°").replace(" degree", "°")
    q = re.sub(r'\s+', ' ', q).strip()
    return q

# === Number sanitization ===
def _sanitize_num_str(s):
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s)
    s = str(s).replace(",", "")
    s = re.sub(r"\s*cm\s*$", "", s, flags=re.IGNORECASE)
    s = s.replace("°", "").replace("deg", "").strip()
    s = re.sub(r"[^\d\.\-eE]+$", "", s)
    try:
        return float(s)
    except:
        return None

# === Geometry math helpers ===
def law_of_cosine_angle(a,b,c):
    denom = 2*b*c
    val = (b*b + c*c - a*a)/denom if denom!=0 else 1
    val = min(1,max(-1,val))
    return math.degrees(math.acos(val))

def law_of_cosine_side(b,c,A_deg):
    A = math.radians(A_deg)
    return math.sqrt(b*b + c*c - 2*b*c*math.cos(A))

def law_of_sines_side(a,A_deg,B_deg):
    return a * math.sin(math.radians(B_deg)) / math.sin(math.radians(A_deg))

# === Drawing functions ===
def draw_SSS(sides, points):
    A,B,C = points
    AB = sides.get(f"{A}{B}") or sides.get(f"{B}{A}")
    BC = sides.get(f"{B}{C}") or sides.get(f"{C}{B}")
    AC = sides.get(f"{A}{C}") or sides.get(f"{C}{A}")
    if not all([AB,BC,AC]): return None
    P1 = (0.0,0.0)
    P2 = (AB,0.0)
    d = AB
    if d==0 or (AC+BC < d) or (abs(AC-BC)>d): return None
    a = (AC*AC - BC*BC + d*d)/(2*d)
    h = math.sqrt(max(0.0, AC*AC - a*a))
    xm = a/d*(P2[0]-P1[0]) + P1[0]
    ym = a/d*(P2[1]-P1[1]) + P1[1]
    rx = -(P2[1]-P1[1])*(h/d)
    ry = (P2[0]-P1[0])*(h/d)
    P3 = (xm+rx, ym+ry)
    return P1,P2,P3

def draw_SAS(sides, angles, points):
    A,B,C = points
    AB = sides.get(f"{A}{B}") or sides.get(f"{B}{A}")
    BC = sides.get(f"{B}{C}") or sides.get(f"{C}{B}")
    angle_val = next((v for k,v in angles.items() if len(k)>=3 and k[1]==B), None)
    if not (AB and BC and angle_val): return None
    P1 = (0.0, 0.0)
    P2 = (AB, 0.0)
    theta = math.radians(180 - angle_val)
    Px = P2[0] + BC*math.cos(theta)
    Py = P2[1] + BC*math.sin(theta)
    P3 = (Px, Py)
    return P1,P2,P3

def draw_ASA_AAS(sides, angles, points):
    A,B,C = points
    if not sides or len(angles)<2: return None
    side_key = next(iter(sides.keys()))
    side_length = sides[side_key]
    p1, p2 = side_key[0], side_key[1]
    angle_at = {k[1]: v for k,v in angles.items() if len(k)>=3}
    if p1 in angle_at and p2 in angle_at:
        angleA = angle_at[p1]
        angleB = angle_at[p2]
        angleC = 180-(angleA+angleB)
        if angleC<=0: return None
        AC = side_length*math.sin(math.radians(angleB))/math.sin(math.radians(angleC))
        BC = side_length*math.sin(math.radians(angleA))/math.sin(math.radians(angleC))
        P1 = (0.0, 0.0)
        P2 = (side_length, 0)
        d = side_length
        a = (AC*AC - BC*BC + d*d)/(2*d)
        h = math.sqrt(max(0.0, AC*AC - a*a))
        xm = a/d*(P2[0]-P1[0]) + P1[0]
        ym = a/d*(P2[1]-P1[1]) + P1[1]
        rx = -(P2[1]-P1[1])*(h/d)
        ry = (P2[0]-P1[0])*(h/d)
        P3 = (xm+rx, ym+ry)
        mapping = {p1:P1, p2:P2}
        remaining = next(lbl for lbl in points if lbl not in (p1,p2))
        mapping[remaining] = P3
        return mapping[points[0]], mapping[points[1]], mapping[points[2]]
    return None

def draw_SSA(sides, angles, points):
    A,B,C = points
    if len(sides)<2: return None
    sideA = next(((k,v) for k,v in sides.items() if A in k), None)
    if not sideA: return None
    kA,valA = sideA
    angleA = next((v for k,v in angles.items() if len(k)>=3 and k[1]==A), None)
    other_side = next(((k,v) for k,v in sides.items() if k!=kA), None)
    if not (angleA and other_side): return None
    base_label1, base_label2 = kA[0], kA[1]
    base_length = valA
    P1 = (0.0, 0.0)
    P2 = (base_length, 0.0)
    s = other_side[1]
    theta = math.radians(angleA)
    P3 = (P1[0] + s*math.cos(theta), P1[1] + s*math.sin(theta))
    return P1,P2,P3

# === Normalize & infer missing data ===
def normalize_and_infer(raw):
    if not raw or not isinstance(raw, dict):
        return None
    points = raw.get("points", [])
    if len(points) != 3:
        return None
    sides_raw = raw.get("sides", {}) or {}
    angles_raw = raw.get("angles", {}) or {}
    sides = {}
    angles = {}
    for k,v in sides_raw.items():
        val = _sanitize_num_str(v)
        if val is not None:
            sides[k.upper()] = float(val)
    for k,v in angles_raw.items():
        val = _sanitize_num_str(v)
        if val is not None:
            angles[k.upper()] = float(val)
    detected = raw.get("triangle_type")
    if detected:
        detected = detected.upper()

    if len(sides) == 3:
        return {"points": points, "sides": sides, "angles": angles, "triangle_type": "SSS"}

    if len(angles) >= 2 and len(sides) == 1:
        side_key = next(iter(sides.keys()))
        side_len = sides[side_key]
        p1, p2 = side_key[0], side_key[1]
        angle_at = {k[1]: v for k,v in angles.items() if len(k)>=3}
        if p1 in angle_at and p2 in angle_at:
            angleA = angle_at[p1]
            angleB = angle_at[p2]
            angleC = 180 - (angleA + angleB)
            if angleC <= 0:
                return None
            remaining = next(lbl for lbl in points if lbl not in (p1,p2))
            try:
                AC = side_len*math.sin(math.radians(angleB))/math.sin(math.radians(angleC))
                BC = side_len*math.sin(math.radians(angleA))/math.sin(math.radians(angleC))
            except:
                return None
            sides_filled = sides.copy()
            sides_filled[f"{p1}{remaining}"] = AC
            sides_filled[f"{p2}{remaining}"] = BC
            angles_filled = angles.copy()
            angles_filled[f"{p1}{remaining}{p2}"] = angleC
            return {"points": points, "sides": sides_filled, "angles": angles_filled, "triangle_type": "ASA" if not detected else detected}

    if len(sides) == 2 and len(angles) == 1:
        only_angle_key = next(iter(angles.keys()))
        mid = only_angle_key[1] if len(only_angle_key)>=3 else None
        side_keys = list(sides.keys())
        if mid and all(any(mid == ch for ch in k) for k in side_keys):
            side_list = [(k,v) for k,v in sides.items() if mid in k]
            if len(side_list) >= 2:
                (k1,s1), (k2,s2) = side_list[0], side_list[1]
                other1 = k1[0] if k1[1]==mid else k1[1]
                other2 = k2[0] if k2[1]==mid else k2[1]
                A_deg = angles[only_angle_key]
                try:
                    a = law_of_cosine_side(s1,s2,A_deg)
                except:
                    return None
                sides_filled = sides.copy()
                sides_filled[f"{other1}{other2}"] = a
                return {"points": points, "sides": sides_filled, "angles": angles, "triangle_type": "SAS" if not detected else detected}
        else:
            # SSA heuristic fallback: just return cleaned data
            return {"points": points, "sides": sides, "angles": angles, "triangle_type": "SSA" if not detected else detected}

    return {"points": points, "sides": sides, "angles": angles, "triangle_type": detected}

# === Infer triangle type for drawing ===
def infer_triangle_type(sides, angles, detected_type):
    if detected_type:
        return detected_type
    if len(sides) == 3:
        return "SSS"
    if len(sides) == 2 and len(angles) == 1:
        only_angle_key = next(iter(angles.keys())) if angles else None
        mid = only_angle_key[1] if only_angle_key and len(only_angle_key) >=3 else None
        if mid and all(any(mid == ch for ch in k) for k in sides.keys()):
            return "SAS"
        return "SSA"
    if len(angles) == 2 and len(sides) == 1:
        side_key = next(iter(sides.keys()))
        mid = side_key[1]
        return "ASA" if any(mid == k[1] for k in angles.keys()) else "AAS"
    return None

# === Point & side labeling helpers ===
def label_point(ax, point, label, ha='center', va='center', fontsize=10):
    ax.text(point[0], point[1], label, fontsize=fontsize, ha=ha, va=va, backgroundcolor='white')

def label_midpoint(ax, p1, p2, text, fontsize=8):
    mx, my = (p1[0]+p2[0])/2, (p1[1]+p2[1])/2
    ax.text(mx, my, text, fontsize=fontsize, ha='center', va='center', backgroundcolor='white')

# === Unified draw_triangle orchestrator ===
def draw_triangle(points, sides, angles, detected_type=None):
    try:
        ttype = infer_triangle_type(sides, angles, detected_type)
        draw_func = {
            "SSS": lambda: draw_SSS(sides, points),
            "SAS": lambda: draw_SAS(sides, angles, points),
            "ASA": lambda: draw_ASA_AAS(sides, angles, points),
            "AAS": lambda: draw_ASA_AAS(sides, angles, points),
            "SSA": lambda: draw_SSA(sides, angles, points)
        }.get(ttype, lambda: draw_SAS(sides, angles, points))

        res = draw_func()
        if not res:
            return None

        P1, P2, P3 = res

        fig, ax = plt.subplots(figsize=(FIG_INCH, FIG_INCH))
        ax.set_aspect('equal')
        ax.axis('off')
        ax.plot([P1[0], P2[0]], [P1[1], P2[1]], 'b-')
        ax.plot([P2[0], P3[0]], [P2[1], P3[1]], 'b-')
        ax.plot([P3[0], P1[0]], [P3[1], P1[1]], 'b-')

        # Mark vertices
        label_point(ax, P1, points[0], ha='right', va='top')
        label_point(ax, P2, points[1], ha='left', va='top')
        label_point(ax, P3, points[2], ha='center', va='bottom')

        # Mark sides length
        label_midpoint(ax, P1, P2, f"{round(sides.get(f'{points[0]}{points[1]}', sides.get(f'{points[1]}{points[0]}', 0)),2)} cm")
        label_midpoint(ax, P2, P3, f"{round(sides.get(f'{points[1]}{points[2]}', sides.get(f'{points[2]}{points[1]}', 0)),2)} cm")
        label_midpoint(ax, P3, P1, f"{round(sides.get(f'{points[2]}{points[0]}', sides.get(f'{points[0]}{points[2]}', 0)),2)} cm")

        # Mark angles
        for k,v in angles.items():
            if len(k) >= 3:
                vertex = k[1]
                angle_val = v
                # get vertex coordinate
                idx = points.index(vertex)
                vertex_point = [P1,P2,P3][idx]
                offset = 0.3
                ax.text(vertex_point[0]+offset, vertex_point[1]+offset, f"{int(angle_val)}°", fontsize=10, color='r')

        buf = BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)
        img = PIL.Image.open(buf)
        return img
    except Exception as e:
        print("Error in draw_triangle:", e)
        return None

# === Main Streamlit app ===
def main():
    st.title("LLM Math Solver with Geometry Sketch")

    user_input = st.text_area("Enter your math or geometry question:")

    if st.button("Solve"):
        clean_q = clean_input_text(user_input)

        # Detect geometry keywords
        if any(kw in clean_q.lower() for kw in GEOMETRY_KEYWORDS):
            st.info("Detected geometry-related question. Extracting triangle data...")
            raw_json = extract_triangle_json(clean_q)
            data = normalize_and_infer(raw_json)
            if data:
                st.success(f"Detected Triangle Type: **{data['triangle_type']}**")
                st.write("### Extracted Data:")
                st.json(data)

                img = draw_triangle(data['points'], data['sides'], data['angles'], data['triangle_type'])
                if img:
                    st.image(img, caption="Triangle Sketch")
                else:
                    st.error("Failed to generate triangle sketch.")
            else:
                st.error("Failed to extract triangle data from question.")
        else:
            st.info("Generating step-by-step solution using LLM...")
            answer = query_llm_solution(clean_q)
            st.markdown(answer)

if __name__ == "__main__":
    main()
