import streamlit as st
import requests
import re
import matplotlib.pyplot as plt
from io import BytesIO

# Define subjects with their prompts
SUBJECTS = {
    "Math": {
        "icon": "🧮",
        "prompt": "You are a math tutor. Provide detailed step-by-step explanations, show all work, and use proper mathematical notation. Format answers as textbook-style solutions with clear sections."
    },
    "Physics": {
        "icon": "🧪",
        "prompt": "You are a physics tutor. Explain concepts clearly, show all equations and derivations, and use proper SI units. Format answers as textbook-style solutions with clear sections."
    },
    "Chemistry": {
        "icon": "🧪",
        "prompt": "You are a chemistry tutor. Explain concepts clearly, show all equations and reactions, and use proper chemical notation. Format answers as textbook-style solutions with clear sections."
    },
    "Biology": {
        "icon": "🧬",
        "prompt": "You are a biology tutor. Explain concepts clearly, show all diagrams and processes, and use proper biological terminology. Format answers as textbook-style solutions with clear sections."
    }
}

def should_show_diagram(question, subject):
    """Determine if a diagram is needed based on the question content."""
    keywords = ["draw", "diagram", "graph", "plot", "sketch", "visualize"]
    return any(keyword in question.lower() for keyword in keywords)

def create_smart_visualization(question, subject):
    """Generate appropriate visualization based on the subject and question."""
    try:
        plt.style.use('ggplot')
        fig, ax = plt.subplots()
        
        if subject == "Math":
            # Simple math visualization
            x = [1, 2, 3, 4, 5]
            y = [2, 4, 6, 8, 10]
            ax.plot(x, y, marker='o', color='blue')
            ax.set_title("Math Visualization")
            ax.set_xlabel("X-axis")
            ax.set_ylabel("Y-axis")
        
        elif subject == "Physics":
            # Physics graph (e.g., velocity vs time)
            t = [0, 1, 2, 3, 4]
            v = [0, 5, 10, 15, 20]
            ax.plot(t, v, color='red', linestyle='--', marker='s')
            ax.set_title("Velocity vs Time")
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Velocity (m/s)")
        
        elif subject == "Chemistry":
            # Chemical reaction visualization
            ax.bar(['Reactants', 'Products'], [10, 15], color=['blue', 'green'])
            ax.set_title("Chemical Reaction")
            ax.set_ylabel("Amount (mol)")
        
        elif subject == "Biology":
            # Cell structure diagram
            ax.set_aspect('equal')
            ax.add_patch(plt.Circle((0.5, 0.5), 0.4, color='lightblue', label='Nucleus'))
            ax.add_patch(plt.Rectangle((0.1, 0.1), 0.2, 0.2, color='green', label='Mitochondria'))
            ax.add_patch(plt.Polygon([[0.3, 0.3], [0.5, 0.5], [0.3, 0.7]], color='orange', label='Ribosomes'))
            ax.set_title("Cell Structure")
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
        
        # Customize plot
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(0.8)
        ax.spines['bottom'].set_linewidth(0.8)
        
        # Save plot
        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', dpi=150, 
                   facecolor='white', edgecolor='none')
        plt.close()
        return buf
        
    except Exception as e:
        return None

def format_textbook_response(response_text, subject):
    """Format response in clean textbook style with proper fractions and math notation."""
    # Clean up all LaTeX and broken formatting
    formatted = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', response_text)
    formatted = re.sub(r'\\sqrt\{([^}]+)\}', r'√(\1)', formatted)
    formatted = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', formatted)
    formatted = re.sub(r'\\[a-zA-Z]+', '', formatted)
    
    # Fix broken HTML spans
    formatted = re.sub(r'<span[^>]*>', '', formatted)
    formatted = re.sub(r'</span>', '', formatted)
    
    # Create proper fractions
    def create_proper_fraction(numerator, denominator):
        """Create proper fraction with numerator over denominator"""
        return f'''<div style="display: inline-block; text-align: center; vertical-align: middle; margin: 0 8px; font-family: 'Times New Roman', serif; color: #000000;">
            <div style="padding: 2px 8px; border-bottom: 2px solid #000000; margin-bottom: 2px; line-height: 1.2;">{numerator.strip()}</div>
            <div style="padding: 2px 8px; line-height: 1.2;">{denominator.strip()}</div>
        </div>'''
    
    formatted = re.sub(r'\(([^)]+)\)/\(([^)]+)\)', 
                      lambda m: create_proper_fraction(m.group(1), m.group(2)), 
                      formatted)
    
    # Simple variable fractions
    formatted = re.sub(r'\b([a-zA-Z0-9²³]+)/([a-zA-Z0-9²³]+)\b', 
                      lambda m: create_proper_fraction(m.group(1), m.group(2)), 
                      formatted)
    
    # Fix exponents
    formatted = re.sub(r'\^2', '²', formatted)
    formatted = re.sub(r'\^3', '³', formatted)
    formatted = re.sub(r'\^(\d)', r'<sup>\1</sup>', formatted)
    
    # Clean up extra spaces and formatting
    formatted = re.sub(r'\s+', ' ', formatted)
    
    return formatted

def get_api_response(question, subject):
    """Get response from API with error handling."""
    try:
        # Simulate API call (replace with actual API endpoint)
        response = {
            "Math": "The solution involves... (showing all steps with proper formatting)",
            "Physics": "The derivation starts with... (including all equations)",
            "Chemistry": "The reaction mechanism is... (with proper chemical notation)",
            "Biology": "The process involves... (with detailed diagrams)"
        }.get(subject, "Subject not supported")
        
        return response
    
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    st.set_page_config(page_title="Academic Assistant", layout="wide")
    
    st.markdown("""
        <style>
        .reportview-container {
            background: #f5f5f5;
        }
        .sidebar .sidebar-content {
            background: #ffffff;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("📚 Academic Assistant")
    st.markdown("Get detailed solutions for math, physics, chemistry, and biology questions.")
    
    subject = st.selectbox("Select Subject", list(SUBJECTS.keys()))
    question = st.text_area("Enter your question", height=150)
    
    if st.button("Get Solution"):
        if not question:
            st.warning("Please enter a question.")
        else:
            response = get_api_response(question, subject)
            formatted_response = format_textbook_response(response, subject)
            
            st.markdown("### 📝 Solution:")
            st.markdown(formatted_response, unsafe_allow_html=True)
            
            if should_show_diagram(question, subject):
                visualization = create_smart_visualization(question, subject)
                if visualization:
                    st.markdown("### 📊 Visualization:")
                    st.image(visualization, use_column_width=True)
                else:
                    st.warning("No suitable visualization available for this question.")
            else:
                st.info("No diagram needed for this question.")
    
    st.markdown("""
        <div style="text-align: center; margin-top: 40px;">
            <p>© 2023 Academic Assistant. All rights reserved.</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
