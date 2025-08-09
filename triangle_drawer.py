import streamlit as st
import requests
import matplotlib.pyplot as plt
import numpy as np
import json
from io import BytesIO
import PIL.Image

# === API Setup ===
API_URL = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": "Bearer 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",
    "Content-Type": "application/json"
}

# === LLM Call (for solutions) ===
# === LLM Call (for solutions) ===
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
    response = requests.post(API_URL, headers=headers, json=payload)

    try:
        result = response.json()
    except Exception:
        return f"❌ API did not return JSON. Raw output:\n{response.text}"

    if "choices" in result and result["choices"]:
        return result["choices"][0]["message"]["content"]
    else:
        return f"❌ API Error:\n{json.dumps(result, indent=2)}"

# === LLM Call (for triangle data extraction) ===
def extract_triangle_json(question):
    prompt = f"""
You are an assistant that extracts triangle construction parameters from a geometry question.

Task:
1. Identify the triangle's three points (vertices).
2. Extract given side lengths as a dictionary like {{"AB": 5}}.
3. Extract given angles as a dictionary like {{"ABC": 60}}.
4. Detect the triangle type (SSS, SAS, ASA, SSA, AAS) based on what's given.

Only return a pure JSON object.
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
    response = requests.post(API_URL, headers=headers, json=payload)

    try:
        result = response.json()
    except Exception:
        return {"error": f"❌ API did not return JSON. Raw output:\n{response.text}"}

    if "choices" in result and result["choices"]:
        try:
            return json.loads(result["choices"][0]["message"]["content"])
        except Exception as e:
            return {"error": f"❌ JSON parsing failed: {str(e)}", "raw": result}
    else:
        return {"error": "❌ API Error", "raw": result}



# === Triangle Drawing ===
def draw_triangle(points, sides, angles):
    if not (points and sides and angles):
        return None

    try:
        A, B, C = points[:3]
        side1 = sides.get(f"{A}{B}") or sides.get(f"{B}{A}")
        side2 = sides.get(f"{B}{C}") or sides.get(f"{C}{B}")

        angle_key = None
        for k in angles:
            if B in k and A in k and C in k:
                angle_key = k
                break

        angle = angles.get(angle_key)

        if not (side1 and side2 and angle):
            return None

        angle_rad = np.radians(angle)
        P1 = (0, 0)
        P2 = (side1, 0)
        Px = side1 - side2 * np.cos(angle_rad)
        Py = side2 * np.sin(angle_rad)
        P3 = (Px, Py)

        fig, ax = plt.subplots(figsize=(2.5, 2.5), dpi=100)

        coords = np.array([P1, P2, P3, P1])
        ax.plot(coords[:, 0], coords[:, 1], 'b-', linewidth=2)
        ax.text(*P1, A, fontsize=9, ha='right', va='top')
        ax.text(*P2, B, fontsize=9, ha='left', va='top')
        ax.text(*P3, C, fontsize=9, ha='center', va='bottom')

        # Side lengths
        ax.text((P1[0]+P2[0])/2, (P1[1]+P2[1])/2 - 0.3, f"{side1} cm", fontsize=7, ha='center')
        ax.text((P2[0]+P3[0])/2 + 0.3, (P2[1]+P3[1])/2, f"{side2} cm", fontsize=7, ha='center')
        ax.text((P3[0]+P1[0])/2 - 0.3, (P3[1]+P1[1])/2 + 0.3, f"{round(np.linalg.norm(np.array(P3)-np.array(P1)),1)} cm", fontsize=7, ha='center')

        # Angle arc at point B
        arc_radius = 0.7
        angle_arc = np.linspace(0, angle_rad, 100)
        arc_x = P2[0] + arc_radius * np.cos(angle_arc)
        arc_y = P2[1] + arc_radius * np.sin(angle_arc)
        ax.plot(arc_x, arc_y, 'r-', linewidth=1)

        # Angle label
        angle_label_x = P2[0] + arc_radius * np.cos(angle_rad / 2)
        angle_label_y = P2[1] + arc_radius * np.sin(angle_rad / 2)
        ax.text(angle_label_x, angle_label_y, f"{angle}°", fontsize=8, color='red')

        ax.set_aspect('equal')
        ax.axis('off')
        return fig
    except:
        return None

# === Streamlit UI ===
st.set_page_config(layout="wide")
st.title("📘 Ask a Math Question (Formatted Solver)")

math_type = st.selectbox("Choose the math subject:", [
    "Algebra", "Geometry", "Calculus", "Trigonometry",
    "Arithmetic", "Probability", "Statistics", "Linear Algebra", "Other"])

question = st.text_area("Enter your math question", height=180)


def clean_question(q):
    return q.strip().split(".")[0]

if question:
    st.write("🔍 Solving...")



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

    answer = query_llm_solution(full_prompt)
    st.markdown("### 📘 Answer:")
    st.markdown(answer, unsafe_allow_html=True)

    if math_type == "Geometry" and any(w in question.lower() for w in ["draw", "construct", "sketch"]):
        cleaned = clean_question(question)
        data = extract_triangle_json(cleaned)
        if "triangle_type" in data:
            st.success(f"🧠 Detected Triangle Type: **{data['triangle_type']}**")
            if data and all(k in data for k in ["points", "sides", "angles"]):
                if st.button("Generate Triangle Sketch"):
                    fig = draw_triangle(data["points"], data["sides"], data["angles"])
                    if fig:
                        buf = BytesIO()
                        fig.savefig(buf, format="png", bbox_inches="tight", dpi=150)
                        buf.seek(0)
                        img = PIL.Image.open(buf)

                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st.image(img, caption="Constructed Triangle", width=400)

                    st.markdown("**Final Answer**\n\nTriangle sketch constructed with labeled vertices, side lengths, and given dimensions.")
                else:
                    st.warning("❌ Could not construct triangle — side/angle names do not match detected pattern.")
        else:
            st.info("ℹ️ Please mention at least 2 sides and 1 angle clearly for the triangle sketch.")







#Sketch an equilateral triangle of side 5 cm using compass and straightedge. Label it as triangle DEF

#Draw a triangle PQR in which PQ = 4 cm, QR = 5 cm, and ∠PQR = 90°. Mark all vertices clearly.
